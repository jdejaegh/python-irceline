import asyncio
import socket
from abc import ABC, abstractmethod
from typing import Tuple, List, Set
from xml.etree import ElementTree

import aiohttp
import async_timeout
from aiohttp import ClientResponse

from .data import IrcelineFeature

_rio_wfs_base_url = 'https://geo.irceline.be/wfs'
_forecast_wms_base_url = 'https://geo.irceline.be/forecast/wms'
_rio_ifdm_wms_base_url = 'https://geobelair.irceline.be/rioifdm/wms'
_user_agent = 'github.com/jdejaegh/python-irceline'


class IrcelineApiError(Exception):
    """Exception to indicate an API error."""


class IrcelineBaseClient(ABC):
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    @abstractmethod
    async def get_data(self,
                       features: List[IrcelineFeature],
                       position: Tuple[float, float]) -> dict:
        pass

    @abstractmethod
    def get_capabilities(self) -> Set[str]:
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


class IrcelineBaseWmsClient(IrcelineBaseClient, ABC):
    _default_querystring = {"service": "WMS",
                            "version": "1.1.1",
                            "request": "GetFeatureInfo",
                            "info_format": "application/json",
                            "width": "1",
                            "height": "1",
                            "srs": "EPSG:4326",
                            "X": "1",
                            "Y": "1"}
    _epsilon = 0.00001
    _base_url = None

    @staticmethod
    def _parse_capabilities(xml_string: str) -> Set[str]:
        try:
            root = ElementTree.fromstring(xml_string)
        except ElementTree.ParseError:
            return set()

        path = './/Capability/Layer/Layer/Name'
        feature_type_names = {t.text for t in root.findall(path)}
        return feature_type_names

    async def get_capabilities(self) -> Set[str]:
        """
        Fetch the list of possible features from the WMS server
        :return: set of features available on the WMS server
        """
        querystring = {"service": "WMS",
                       "version": "1.1.1",
                       "request": "GetCapabilities"}
        r: ClientResponse = await self._api_wrapper(self._base_url, querystring)

        return self._parse_capabilities(await r.text())
