"""The BWT model check."""


from enum import Enum
import aiohttp
import logging

from bwt_api.exception import ConnectException

class BwtModel(Enum):
    """Enum for BWT models."""
    PERLA_LOCAL_API = 1
    PERLA_SILK = 2
    SMART_DOS = 3

async def determine_bwt_model(host: str, logger: logging.Logger = logging.getLogger(__name__)) -> BwtModel:
    """Determine the BWT model based on the api response."""

    logger.info("Determining BWT model for host %s", host)
    timeout = aiohttp.ClientTimeout(total=3)

    # Recent BWT Perla models with local API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:8080/api", timeout=timeout) as response:
                res = await response.text()
                logger.debug("Response from %s:8080/api: %s - %s", host, response.status, res)
                if response.status == 404 and res == "Not Found":
                    logger.info("Detected BWT Perla model with local API at %s", host)
                    return BwtModel.PERLA_LOCAL_API
    except Exception:
        pass

    # Perla Silk with registers endpoint that returns a list of raw data
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:80/silk/registers", timeout=timeout) as response:
                res = await response.text()
                logger.debug("Response from %s:80/silk/registers: %s - %s", host, response.status, res)
                if response.status == 200 and res.startswith("""{"params":["""):
                    logger.info("Detected BWT Perla model with Silk API at %s", host)
                    return BwtModel.PERLA_SILK
    except Exception:
        pass

    # Smart Dos
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}:80/api/v1/gatt/0201", timeout=timeout) as response:
                res = await response.text()
                logger.debug("Response from %s:80/api/v1/gatt/0201: %s - %s", host, response.status, res)
                if response.status == 200 and res.startswith("""{"""):
                    logger.info("Detected BWT Smart Dos model at %s", host)
                    return BwtModel.SMART_DOS
    except Exception:
        pass

    raise ConnectException(f"Could not determine BWT model for host {host}. Please check the connection or the host address.")
