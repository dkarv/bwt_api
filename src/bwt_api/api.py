import aiohttp
import asyncio
import base64
from bwt_api.error import BwtError
from bwt_api.exception import WrongCodeException

from bwt_api.data import CurrentResponse, DailyResponse, MonthlyResponse, YearlyResponse
from bwt_api.data import Hardness


class BwtApi:
    def __init__(self, host, code):
        self.host = host
        self.code = code
        auth = f"user:{code}"
        base64_auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        self.headers = {"Authorization": f"Basic {base64_auth}"}

    async def get_data(self, endpoint):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"http://{self.host}:8080/api/{endpoint}"
            ) as response:
                print(f"Status: {response.status}")
                print(f"Content-type: {response.headers['content-type']}")
                match response.status:
                    case 404:
                        raise WrongCodeException()
                    case 200:
                        json = await response.json(content_type=None)
                        print(f"Raw response: {json}")
                        return json
                    case _:
                        print(f"Unknown response: {response.text()}")
                        raise Exception("Unknown response")

    async def get_current_data(self) -> CurrentResponse:
        print(f"Fetching current data from {self.host}")
        raw = await self.get_data("GetCurrentData")
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
        print(f"Fetching daily data from {self.host}")
        raw = await self.get_data("GetDailyData")
        keys = [
            f"{min // 60:02}{min % 60:02}_{min // 60:02}{min % 60 + 29:02}_l"
            for min in range(0, 1440, 30)
        ]
        return DailyResponse(list(map(lambda k: raw[k], keys)))

    async def get_monthly_data(self) -> MonthlyResponse:
        print(f"Fetching monthly data from {self.host}")
        raw = await self.get_data("GetMonthlyData")
        keys = [f"Day{day:02}_l" for day in range(1, 32)]
        return MonthlyResponse(list(map(lambda k: raw[k], keys)))

    async def get_yearly_data(self) -> YearlyResponse:
        print(f"Fetching yearly data from {self.host}")
        raw = await self.get_data("GetYearlyData")
        keys = [f"Month{month:02}_l" for month in range(1, 13)]
        return YearlyResponse(list(map(lambda k: raw[k], keys)))
