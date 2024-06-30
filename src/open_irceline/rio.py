import asyncio
from datetime import datetime, date, UTC, timedelta
from typing import List, Tuple, Dict, Set
from xml.etree import ElementTree

from aiohttp import ClientResponse, ClientResponseError

from .api import IrcelineBaseClient, _rio_wfs_base_url, IrcelineApiError, _rio_ifdm_wms_base_url, IrcelineBaseWmsClient
from .data import RioFeature, FeatureValue, RioIfdmFeature
from .utils import epsg_transform


class IrcelineRioClient(IrcelineBaseClient):
    """
    API client for RIO interpolated IRCEL - CELINE open data
    RIO is more coarse grained for interpolation than RIO IFDM and allows to request multiple features in the same
        request, which may be faster.
    """

    async def get_data(self,
                       features: List[RioFeature],
                       position: Tuple[float, float],
                       timestamp: datetime | date | None = None
                       ) -> Dict[RioFeature, FeatureValue]:
        """
        Call the WFS API to get the interpolated level of RioFeature. Raises exception upon API error
        :param timestamp: datetime for which to get the data for
        :param features: list of RioFeature to fetch from the API
        :param position: decimal degrees pair of coordinates
        :return: dict with the response (key is RioFeature, value is FeatureValue with actual value and timestamp)
        """
        if timestamp is None:
            timestamp = datetime.now(UTC)
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

    async def get_capabilities(self) -> Set[str]:
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


class IrcelineRioIfdmClient(IrcelineBaseWmsClient):
    """
    API client for RIO IFDM interpolated IRCEL - CELINE open data
    RIO IFDM is more fine-grained for interpolation than RIO but only allows one feature to be request at a time, which
    may be slower
    """
    _base_url = _rio_ifdm_wms_base_url

    async def get_data(self,
                       features: List[RioIfdmFeature],
                       position: Tuple[float, float]
                       ) -> Dict[RioIfdmFeature, FeatureValue]:
        """
        Get interpolated concentrations for the given features at the given position.
        :param features: pollutants to get the forecasts for
        :param position: (lat, long)
        :return: dict where key is RioIfdmFeature and value is a FeatureValue
        """
        result = dict()
        lat, lon = position
        base_querystring = (self._default_querystring |
                            {"bbox": f"{lon},{lat},{lon + self._epsilon},{lat + self._epsilon}"})

        tasks = [asyncio.create_task(self._get_single_feature(base_querystring, feature)) for feature in features]
        results = await asyncio.gather(*tasks)

        for r in results:
            result |= r

        return result

    async def _get_single_feature(self, base_querystring: dict, feature: RioIfdmFeature) -> dict:
        result = dict()
        querystring = base_querystring | {"layers": f"{feature}", "query_layers": f"{feature}"}
        try:
            r: ClientResponse = await self._api_wrapper(self._base_url, querystring)
            r: dict = await r.json()
            result[feature] = FeatureValue(
                value=r.get('features', [{}])[0].get('properties', {}).get('GRAY_INDEX'),
                timestamp=datetime.fromisoformat(r.get('timeStamp')) if 'timeStamp' in r else None)
        except (IrcelineApiError, ClientResponseError, IndexError):
            result[feature] = FeatureValue(value=None, timestamp=None)
        return result
