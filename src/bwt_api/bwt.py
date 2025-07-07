"""The BWT model check."""


from enum import Enum
import aiohttp
import logging

from bwt_api.exception import ConnectException

_logger = logging.getLogger(__name__)

class BwtModel(Enum):
    """Enum for BWT models."""
    PERLA_LOCAL_API = 1
    PERLA_SILK = 2

async def determine_bwt_model(host: str) -> BwtModel:
    """Determine the BWT model based on the api response."""

    _logger.debug(f"Determining BWT model for host {host}")
    timeout = aiohttp.ClientTimeout(total=3)
    # Try :8080/api/GetCurrentData
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:8080/api", timeout=timeout) as response:
                res = await response.text()
                _logger.debug(f"Response from {host}:8080/api: {response.status} - {res}")
                if response.status == 404 and res == "Not Found":
                    return BwtModel.PERLA_LOCAL_API
    except Exception:
        pass

    # Try :80/status
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:80/silk/registers", timeout=timeout) as response:
                res = await response.text()
                _logger.debug(f"Response from {host}:80/silk/registers: {response.status} - {res}")
                if response.status == 200 and res.startswith("""{"params":["""):
                    return BwtModel.PERLA_SILK
    except Exception:
        pass

    raise ConnectException(f"Could not determine BWT model for host {host}. Please check the connection or the host address.")
