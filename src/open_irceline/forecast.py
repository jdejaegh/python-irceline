from datetime import date, timedelta, datetime
from itertools import product
from typing import List, Tuple, Dict, Set
from xml.etree import ElementTree

from aiohttp import ClientResponse, ClientResponseError

from .api import IrcelineBaseClient, _forecast_wms_base_url, IrcelineApiError
from .data import ForecastFeature, FeatureValue


class IrcelineForecastClient(IrcelineBaseClient):
    _epsilon = 0.00001

    async def get_data(self,
                       features: List[ForecastFeature],
                       position: Tuple[float, float]
                       ) -> Dict[Tuple[ForecastFeature, date], FeatureValue]:
        """
        Get forecasted concentrations for the given features at the given position. The forecasts are downloaded for
        the specified day and the 3 next days as well
        :param features: pollutants to get the forecasts for
        :param position: (lat, long)
        :return: dict where key is (ForecastFeature, date of the forecast) and value is a FeatureValue
        """
        timestamp = date.today()
        result = dict()
        lat, lon = position
        base_querystring = {"service": "WMS",
                            "version": "1.1.1",
                            "request": "GetFeatureInfo",
                            "info_format": "application/json",
                            "width": "1",
                            "height": "1",
                            "srs": "EPSG:4326",
                            "bbox": f"{lon},{lat},{lon + self._epsilon},{lat + self._epsilon}",
                            "X": "1",
                            "Y": "1"}

        for feature, d in product(features, range(4)):
            querystring = base_querystring | {"layers": f"{feature}_d{d}",
                                              "query_layers": f"{feature}_d{d}"}
            try:
                r: ClientResponse = await self._api_wrapper(_forecast_wms_base_url, querystring)
                r: dict = await r.json()
                result[(feature, timestamp + timedelta(days=d))] = FeatureValue(
                    value=r.get('features', [{}])[0].get('properties', {}).get('GRAY_INDEX'),
                    timestamp=datetime.fromisoformat(r.get('timeStamp')) if 'timeStamp' in r else None)
            except (IrcelineApiError, ClientResponseError, IndexError):
                result[(feature, timestamp + timedelta(days=d))] = FeatureValue(value=None, timestamp=None)

        return result

    async def get_capabilities(self) -> Set[str]:
        """
        Fetch the list of possible features from the WMS server
        :return: set of features available on the WMS server
        """
        querystring = {"service": "WMS",
                       "version": "1.1.1",
                       "request": "GetCapabilities"}
        r: ClientResponse = await self._api_wrapper(_forecast_wms_base_url, querystring)

        return self._parse_capabilities(await r.text())

    @staticmethod
    def _parse_capabilities(xml_string: str) -> Set[str]:
        try:
            root = ElementTree.fromstring(xml_string)
        except ElementTree.ParseError:
            return set()

        path = './/Capability/Layer/Layer/Name'
        feature_type_names = {t.text for t in root.findall(path)}
        return feature_type_names
