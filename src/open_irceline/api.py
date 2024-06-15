import asyncio
import socket
from datetime import datetime, timedelta
from typing import Tuple, List

import aiohttp
from aiohttp import ClientResponse
import async_timeout

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
                            timestamp: datetime,
                            features: List[RioFeature],
                            position: Tuple[float, float]
                            ) -> dict:
        coord = self.epsg_transform(position)
        # Remove one hour from timestamp to handle case where the hour just passed but the data is not yet there
        # (e.g. 5.01 PM, but the most recent data is for 4.00 PM)
        timestamp = timestamp.replace(microsecond=0, second=0, minute=0) - timedelta(hours=1)

        querystring = {"service": "WFS",
                       "version": "1.3.0",
                       "request": "GetFeature",
                       "outputFormat": "application/json",
                       "typeName": ",".join(features),
                       "cql_filter": f"timestamp>='{timestamp.isoformat()}' AND "
                                     f"INTERSECTS(the_geom, POINT ({coord[0]} {coord[1]}))"}

        r: ClientResponse = await self._api_wrapper(rio_wfs_base_url, querystring)
        return self.format_result('rio', await r.json())

    @staticmethod
    def format_result(prefix: str, data: dict) -> dict:
        if data.get('type', None) != 'FeatureCollection' or not isinstance(data.get('features', None), list):
            return dict()
        features = data.get('features', [])
        result = dict()
        for f in features:
            if (f.get('id', None) is None or
                    f.get('properties', {}).get('value', None) is None or
                    f.get('properties', {}).get('timestamp', None) is None):
                continue

            try:
                timestamp = datetime.fromisoformat(f.get('properties', {}).get('timestamp'))
                value = float(f.get('properties', {}).get('value'))
            except (TypeError, ValueError):
                continue

            name = f"{prefix}:{f.get('id').split('.')[0]}"
            if name not in result or result[name]['timestamp'] < timestamp:
                result[name] = FeatureValue(timestamp=timestamp, value=value)

        return result

    async def _api_wrapper(self, url: str, querystring: dict):

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
