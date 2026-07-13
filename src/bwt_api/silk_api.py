"""The BWT Silk API class."""

import aiohttp
import logging

from bwt_api.exception import ApiException, ConnectException

_logger = logging.getLogger(__name__)


class BwtSilkApi:
    """BWT Silk Api."""
    _session: aiohttp.ClientSession
    _host: str

    def __init__(self, host):
        self._host = host
        self._session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *err):
        await self.close()

    async def close(self):
        await self._session.close()

    async def get_registers(self) -> list[int]:
        """Internal method to fetch json from the endpoint and handle general errors."""
        try:
            async with self._session.get(f"http://{self._host}:80/silk/registers") as response:
                _logger.debug(
                    f"Response status: {response.status}, content-type: {response.headers['content-type']}"
                )
                if response.status == 200:
                    json = await response.json(content_type=None)
                    _logger.debug(f"Raw response: {json}")
                    return json["params"]
                else:
                    text = await response.text()
                    _logger.warning(f"Unknown response with status {response.status}: {text}")
                    raise ApiException(f"Unknown response: {text}")
        except aiohttp.ClientConnectorError as e:
            raise ConnectException from e
