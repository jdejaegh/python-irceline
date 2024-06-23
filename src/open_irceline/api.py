import asyncio
import csv
import socket
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date
from io import StringIO
from itertools import product
from typing import Tuple, List, Dict, Set
from xml.etree import ElementTree

import aiohttp
import async_timeout
from aiohttp import ClientResponse

from .data import RioFeature, FeatureValue, ForecastFeature, IrcelineFeature
from .utils import SizedDict, epsg_transform, round_coordinates

_rio_wfs_base_url = 'https://geo.irceline.be/wfs'
# noinspection HttpUrlsUsage
# There is not HTTPS version of this endpoint
_forecast_base_url = 'http://ftp.irceline.be/forecast'
_user_agent = 'github.com/jdejaegh/python-irceline'

class IrcelineApiError(Exception):
    """Exception to indicate an API error."""


class IrcelineBaseClient(ABC):
    def __init__(self, session: aiohttp.ClientSession, cache_size: int = 20) -> None:
        self._session = session
        self._cache = SizedDict(cache_size)

    @abstractmethod
    async def get_data(self,
                       timestamp: datetime | date,
                       features: List[IrcelineFeature],
                       position: Tuple[float, float]) -> dict:
        pass

    async def _api_wrapper(self, url: str, querystring: dict = None, headers: dict = None, method: str = 'GET'):
        """
        Call the URL with the specified query string. Raises exception for >= 400 response code
        :param url: base URL
        :param querystring: dict to build the query string
        :return: response from the client
        """
        if headers is None:
            headers = dict()
        if 'User-Agent' not in headers:
            headers |= {'User-Agent': _user_agent}

        try:
            async with async_timeout.timeout(60):
                response = await self._session.request(
                    method=method,
                    url=url,
                    params=querystring,
                    headers=headers
                )
                response.raise_for_status()
                return response

        except asyncio.TimeoutError as exception:
            raise IrcelineApiError("Timeout error fetching information") from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise IrcelineApiError("Error fetching information") from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise IrcelineApiError(f"Something really wrong happened! {exception}") from exception

    async def _api_cached_wrapper(self, url: str, method: str = 'GET'):
        """
        Call the API but uses cache based on the ETag value to avoid repeated calls for the same ressource
        :param url: url to fetch
        :param method: HTTP method (default to GET)
        :return: response from the client
        """
        if url in self._cache:
            headers = {"If-None-Match": f'{self._cache.get(url, {}).get("etag")}'}
        else:
            headers = None

        r: ClientResponse = await self._api_wrapper(url, headers=headers, method=method)
        if r.status == 304:
            return self._cache.get(url, {}).get("response")
        elif 'ETag' in r.headers:
            self._cache[url] = {'etag': r.headers['ETag'],
                                'response': r}
        return r


class IrcelineRioClient(IrcelineBaseClient):
    """API client for RIO interpolated IRCEL - CELINE open data"""

    async def get_data(self,
                       timestamp: datetime | date,
                       features: List[RioFeature],
                       position: Tuple[float, float]
                       ) -> Dict[RioFeature, FeatureValue]:
        """
        Call the WFS API to get the interpolated level of RioFeature. Raises exception upon API error
        :param timestamp: datetime for which to get the data for
        :param features: list of RioFeature to fetch from the API
        :param position: decimal degrees pair of coordinates
        :return: dict with the response (key is RioFeature, value is FeatureValue with actual value and timestamp)
        """
        # Remove one hour/day from timestamp to handle case where the hour just passed but the data is not yet there
        # (e.g. 5.01 PM, but the most recent data is for 4.00 PM)
        if isinstance(timestamp, datetime):
            timestamp = timestamp.replace(microsecond=0, second=0, minute=0) - timedelta(hours=1)
            timestamp = timestamp.isoformat()
            key = 'timestamp'
        elif isinstance(timestamp, date):
            timestamp = timestamp - timedelta(days=1)
            timestamp = timestamp.isoformat()
            key = 'date'
        else:
            raise IrcelineApiError(f"Wrong parameter type for timestamp: {type(timestamp)}")

        lat, lon = epsg_transform(position)
        querystring = {"service": "WFS",
                       "version": "1.3.0",
                       "request": "GetFeature",
                       "outputFormat": "application/json",
                       "typeName": ",".join(features),
                       "cql_filter":
                           f"{key}>='{timestamp}'"
                           f" AND "
                           f"INTERSECTS(the_geom, POINT ({lat} {lon}))"}
        r: ClientResponse = await self._api_wrapper(_rio_wfs_base_url, querystring)
        return self._format_result('rio', await r.json(), features)

    async def get_rio_capabilities(self) -> Set[str]:
        """
        Fetch the list of possible features from the WFS server
        :return: set of features available on the WFS server
        """
        querystring = {"service": "WFS",
                       "version": "1.3.0",
                       "request": "GetCapabilities"}
        r: ClientResponse = await self._api_wrapper(_rio_wfs_base_url, querystring)

        return self._parse_capabilities(await r.text())

    @staticmethod
    def _parse_capabilities(xml_string: str) -> Set[str]:
        """
        From an XML string obtained with GetCapabilities, generate a set of feature names
        :param xml_string: XML string to parse
        :return: set of FeatureType Names found in the XML document
        """
        try:
            root = ElementTree.fromstring(xml_string)
        except ElementTree.ParseError:
            return set()
        # noinspection HttpUrlsUsage
        # We never connect to the URL, it is just the namespace in the XML
        namespaces = {
            'wfs': 'http://www.opengis.net/wfs',
        }
        path = './/wfs:FeatureTypeList/wfs:FeatureType/wfs:Name'
        feature_type_names = {t.text for t in root.findall(path, namespaces)}
        return feature_type_names

    @staticmethod
    def _format_result(prefix: str, data: dict, features: List[RioFeature]) -> dict:
        """
        Format the JSON dict returned by the WFS service into a more practical dict to use with only the latest measure
        for each feature requested
        :param prefix: namespace of the feature (e.g. rio), without the colon
        :param data: JSON dict value as returned by the API
        :param features: RioFeatures wanted in the final dict
        :return: reduced dict, key is RioFeature, value is FeatureValue
        """
        if data.get('type', None) != 'FeatureCollection' or not isinstance(data.get('features', None), list):
            return dict()
        features_api = data.get('features', [])
        result = dict()
        for f in features_api:
            props = f.get('properties', {})
            if (f.get('id', None) is None or
                    props.get('value', None) is None):
                continue
            if (props.get('timestamp', None) is None and
                    props.get('date', None) is None):
                continue

            try:
                if 'timestamp' in props.keys():
                    timestamp = datetime.fromisoformat(props.get('timestamp'))
                else:
                    # Cut last character as the date is written '2024-06-15Z' which is not ISO compliant
                    timestamp = date.fromisoformat(props.get('date')[:-1])
                value = float(props.get('value'))
            except (TypeError, ValueError):
                continue

            name = f"{prefix}:{f.get('id').split('.')[0]}"
            if name not in [f'{f}' for f in features]:
                continue
            if name not in result or result[name]['timestamp'] < timestamp:
                result[name] = FeatureValue(timestamp=timestamp, value=value)

        return result


class IrcelineForecastClient(IrcelineBaseClient):
    """API client for forecast IRCEL - CELINE open data"""

    async def get_data(self,
                       timestamp: date,
                       features: List[ForecastFeature],
                       position: Tuple[float, float]
                       ) -> Dict[Tuple[ForecastFeature, date], FeatureValue]:
        """
        Get forecasted concentrations for the given features at the given position. The forecasts are downloaded for
        the specified day and the 4 next days as well
        :param timestamp: date at which the forecast are computed (generally today).  If unavailable, the day before will be
        tried as well
        :param features: pollutants to get the forecasts for
        :param position: (lat, long)
        :return: dict where key is (ForecastFeature, date of the forecast) and value is a FeatureValue
        """
        x, y = round_coordinates(position[0], position[1])
        result = dict()

        for feature, d in product(features, range(5)):
            url = f"{_forecast_base_url}/BE_{feature}_{timestamp.strftime('%Y%m%d')}_d{d}.csv"
            try:
                r: ClientResponse = await self._api_cached_wrapper(url)
                ts = timestamp
            except IrcelineApiError:
                # retry for the day before
                yesterday = timestamp - timedelta(days=1)
                url = f"{_forecast_base_url}/BE_{feature}_{yesterday.strftime('%Y%m%d')}_d{d}.csv"
                try:
                    r: ClientResponse = await self._api_cached_wrapper(url)
                    ts = yesterday
                except IrcelineApiError:
                    # if it fails twice, just set None and go to the next
                    result[(feature, timestamp + timedelta(days=d))] = FeatureValue(value=None, timestamp=timestamp)
                    continue

            result[(feature, ts + timedelta(days=d))] = FeatureValue(
                value=self.extract_result_from_csv(x, y, await r.text()),
                timestamp=ts)

        return result

    @staticmethod
    def extract_result_from_csv(x: float, y: float, csv_text: str) -> float | None:
        """
        Find the value of the forecast for the given (x, y) position in the csv text.
        x, y should already be rounded to match the positions found in the csv
        :param x: latitude (rounded)
        :param y: longitude (rounded)
        :param csv_text: text of the CSV file
        :return: value matching the position if found, else None
        """
        f = StringIO(csv_text)
        for row in csv.reader(f, delimiter=';'):
            try:
                if x == float(row[1]) and y == float(row[2]):
                    return float(row[3])
            except (ValueError, IndexError):
                continue
        return None
