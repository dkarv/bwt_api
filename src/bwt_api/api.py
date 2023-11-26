"""The BWT API class."""


from tokenize import String
import aiohttp
import base64
import logging

from bwt_api.error import BwtError
from bwt_api.exception import ApiException, ConnectException, WrongCodeException

from bwt_api.data import CurrentResponse, DailyResponse, MonthlyResponse, YearlyResponse
from bwt_api.data import Hardness

_logger = logging.getLogger(__name__)

class RestApi:
    """Rest functionality encapsulated for testing."""


class BwtApi:
    """BWT Api."""
    _session: aiohttp.ClientSession
    _host: str
    _headers: dict[str,str]

    def __init__(self, host, code):
        self._host = host
        auth = f"user:{code}"
        base64_auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        self._headers = {"Authorization": f"Basic {base64_auth}"}
        self._session = aiohttp.ClientSession(headers=self._headers)
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *err):
        await self.close()

    async def close(self):
        await self._session.close()

    async def __get_data(self, endpoint):
        """Internal method to fetch json from the endpoint and handle general errors."""
        try:
            async with self._session.get(f"http://{self._host}:8080/api/{endpoint}") as response:
                _logger.debug(f"Response status: {response.status}, content-type: {response.headers['content-type']}")
                if (response.status == 200):
                    json = await response.json(content_type=None)
                    _logger.debug(f"Raw response: {json}")
                    return json
                else:
                    text = await response.text()
                    if (response.status == 404 and text == ""):
                        _logger.warning(f"Assuming wrong code: {response}")
                        raise WrongCodeException
                    else:
                        _logger.warning(f"Unknown response with status {response.status}: {text}")
                        raise ApiException(f"Unknown response: {text}")
        except aiohttp.ClientConnectorError as e:
            raise ConnectException from e

    async def get_current_data(self) -> CurrentResponse:
        """Get the current state of the BWT."""
        _logger.debug(f"Fetching current data from {self._host}")
        raw = await self.__get_data("GetCurrentData")
        errors = map(
            lambda error: BwtError(int(error)), raw["ActiveErrorIDs"].split(",")
        )
        in_hardness = Hardness(
            raw["HardnessIN_CaCO3"],
            raw["HardnessIN_dH"],
            raw["HardnessIN_fH"],
            raw["HardnessIN_mmol_l"],
        )
        out_hardness = Hardness(
            raw["HardnessOUT_CaCO3"],
            raw["HardnessOUT_dH"],
            raw["HardnessOUT_fH"],
            raw["HardnessOUT_mmol_l"],
        )
        return CurrentResponse(
            list(errors),
            raw["BlendedWaterSinceSetup_l"],
            raw["CapacityColumn1_ml_dH"],
            raw["CapacityColumn2_ml_dH"],
            raw["CurrentFlowrate_l_h"],
            raw["DosingSinceSetup_ml"],
            raw["FirmwareVersion"],
            in_hardness,
            out_hardness,
            raw["HolidayModeStartTime"],
            raw["LastRegenerationColumn1"],
            raw["LastRegenerationColumn2"],
            raw["LastServiceCustomer"],
            raw["LastServiceTechnican"],
            raw["OutOfService"],
            raw["RegenerationCounterColumn1"],
            raw["RegenerationCounterColumn2"],
            raw["RegenerationCountSinceSetup"],
            raw["RegenerativLevel"],
            raw["RegenerativRemainingDays"],
            raw["RegenerativSinceSetup_g"],
            raw["ShowError"],
            raw["WaterTreatedCurrentDay_l"],
            raw["WaterTreatedCurrentMonth_l"],
            raw["WaterTreatedCurrentYear_l"],
        )

    async def get_daily_data(self) -> DailyResponse:
        """"Get treated water of the current day."""
        _logger.debug(f"Fetching daily data from {self._host}")
        raw = await self.__get_data("GetDailyData")
        # Build the keys. Starting with "00:00_00:39_l" up to "23:30_23:59_l"
        keys = [
            f"{min // 60:02}{min % 60:02}_{min // 60:02}{min % 60 + 29:02}_l"
            for min in range(0, 1440, 30)
        ]
        return DailyResponse(list(map(lambda k: raw[k], keys)))

    async def get_monthly_data(self) -> MonthlyResponse:
        """Get treated water of the current month."""
        _logger.debug(f"Fetching monthly data from {self._host}")
        raw = await self.__get_data("GetMonthlyData")
        keys = [f"Day{day:02}_l" for day in range(1, 32)]
        return MonthlyResponse(list(map(lambda k: raw[k], keys)))

    async def get_yearly_data(self) -> YearlyResponse:
        """Get treated water of the current year."""
        _logger.debug(f"Fetching yearly data from {self._host}")
        raw = await self.__get_data("GetYearlyData")
        keys = [f"Month{month:02}_l" for month in range(1, 13)]
        return YearlyResponse(list(map(lambda k: raw[k], keys)))
