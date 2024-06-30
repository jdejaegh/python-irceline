import asyncio
import socket
from abc import ABC, abstractmethod
from typing import Tuple, List, Set

import aiohttp
import async_timeout

from .data import IrcelineFeature
from .utils import SizedDict

_rio_wfs_base_url = 'https://geo.irceline.be/wfs'
_forecast_wms_base_url = 'https://geo.irceline.be/forecast/wms'
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


