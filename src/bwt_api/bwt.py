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
    SMART_DOS = 3

async def determine_bwt_model(host: str) -> BwtModel:
    """Determine the BWT model based on the api response."""

    _logger.debug(f"Determining BWT model for host {host}")
    timeout = aiohttp.ClientTimeout(total=3)

    # Recent BWT Perla models with local API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:8080/api", timeout=timeout) as response:
                res = await response.text()
                _logger.debug(f"Response from {host}:8080/api: {response.status} - {res}")
                if response.status == 404 and res == "Not Found":
                    return BwtModel.PERLA_LOCAL_API
    except Exception:
        pass

    # Perla Silk with registers endpoint that returns a list of raw data
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:80/silk/registers", timeout=timeout) as response:
                res = await response.text()
                _logger.debug(f"Response from {host}:80/silk/registers: {response.status} - {res}")
                if response.status == 200 and res.startswith("""{"params":["""):
                    return BwtModel.PERLA_SILK
    except Exception:
        pass

    # Smart Dos
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:80/api/v1/gatt/0201", timeout=timeout) as response:
                res = await response.text()
                _logger.debug(f"Response from {host}:80/api/v1/gatt/0201: {response.status} - {res}")
                if response.status == 200 and res.startswith("""{"""):
                    return BwtModel.SMART_DOS
    except Exception:
        pass

    raise ConnectException(f"Could not determine BWT model for host {host}. Please check the connection or the host address.")
