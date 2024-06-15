import asyncio
import socket
from datetime import datetime, timedelta, date
from typing import Tuple, List, Dict

import aiohttp
import async_timeout
from aiohttp import ClientResponse

from . import project_transform, rio_wfs_base_url
from .data import RioFeature, FeatureValue


class IrcelineApiError(Exception):
    """Exception to indicate a general API error."""


class IrcelineApiCommunicationError(IrcelineApiError):
    """Exception to indicate a communication error."""


class IrcelineApiParametersError(IrcelineApiError):
    """Exception to indicate a parameter error."""


class IrcelineClient:
    """API client for IRCEL - CELINE open data"""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    @staticmethod
    def epsg_transform(position: Tuple[float, float]) -> tuple:
        """
        Convert 'EPSG:4326' coordinates to 'EPSG:31370' coordinates
        :param position: (x, y) coordinates
        :return: tuple of int in the EPSG:31370 system
        """
        result = project_transform.transform(position[0], position[1])
        return round(result[0]), round(result[1])

    async def get_rio_value(self,
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
        elif isinstance(timestamp, date):
            timestamp = timestamp - timedelta(days=1)

        coord = self.epsg_transform(position)
        querystring = {"service": "WFS",
                       "version": "1.3.0",
                       "request": "GetFeature",
                       "outputFormat": "application/json",
                       "typeName": ",".join(features),
                       "cql_filter":
                           f"{'timestamp' if isinstance(timestamp, datetime) else 'date'}>='{timestamp.isoformat()}'"
                           f" AND "
                           f"INTERSECTS(the_geom, POINT ({coord[0]} {coord[1]}))"}

        r: ClientResponse = await self._api_wrapper(rio_wfs_base_url, querystring)
        return self.format_result('rio', await r.json(), features)

    @staticmethod
    def format_result(prefix: str, data: dict, features: List[RioFeature]) -> dict:
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

    async def _api_wrapper(self, url: str, querystring: dict):
        """
        Call the URL with the specified query string (GET). Raises exception for >= 400 response code
        :param url: base URL
        :param querystring: dict to build the query string
        :return: response from the client
        """

        headers = {'User-Agent': 'github.com/jdejaegh/python-irceline'}

        try:
            async with async_timeout.timeout(60):
                response = await self._session.request(
                    method='GET',
                    url=url,
                    params=querystring,
                    headers=headers
                )
                response.raise_for_status()
                return response

        except asyncio.TimeoutError as exception:
            raise IrcelineApiCommunicationError("Timeout error fetching information") from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise IrcelineApiCommunicationError("Error fetching information") from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise IrcelineApiError(f"Something really wrong happened! {exception}") from exception
