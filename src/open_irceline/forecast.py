import asyncio
from datetime import date, timedelta, datetime
from itertools import product
from typing import List, Tuple, Dict

from aiohttp import ClientResponse, ClientResponseError

from .api import IrcelineApiError, IrcelineBaseWmsClient, _forecast_wms_base_url
from .data import ForecastFeature, FeatureValue


class IrcelineForecastClient(IrcelineBaseWmsClient):
    _base_url = _forecast_wms_base_url

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
        base_querystring = (self._default_querystring |
                            {"bbox": f"{lon},{lat},{lon + self._epsilon},{lat + self._epsilon}"})

        tasks = [asyncio.create_task(self._get_single_feature(base_querystring, d, feature, timestamp))
                 for feature, d in product(features, range(4))]
        results = await asyncio.gather(*tasks)

        for r in results:
            result |= r

        return result

    async def _get_single_feature(self, base_querystring: dict, d: int, feature: ForecastFeature,
                                  timestamp: date) -> dict:
        result = dict()

        querystring = base_querystring | {"layers": f"{feature}_d{d}",
                                          "query_layers": f"{feature}_d{d}"}
        try:
            r: ClientResponse = await self._api_wrapper(self._base_url, querystring)
            r: dict = await r.json()
            result[(feature, timestamp + timedelta(days=d))] = FeatureValue(
                value=r.get('features', [{}])[0].get('properties', {}).get('GRAY_INDEX'),
                timestamp=datetime.fromisoformat(r.get('timeStamp')) if 'timeStamp' in r else None)
        except (IrcelineApiError, ClientResponseError, IndexError):
            result[(feature, timestamp + timedelta(days=d))] = FeatureValue(value=None, timestamp=None)
        return result
