import pytest

from bwt_api.api import BwtApi
from bwt_api.error import BwtError
from bwt_api.data import CurrentResponse, Hardness
from aioresponses import aioresponses

from bwt_api.exception import ApiException, ConnectException, WrongCodeException

__author__ = "dkarv"
__copyright__ = "dkarv"
__license__ = "MIT"


current_json = """
{
   "ActiveErrorIDs" : "5,32,34",
   "BlendedWaterSinceSetup_l" : 318383,
   "CapacityColumn1_ml_dH" : 5485275,
   "CapacityColumn2_ml_dH" : 3833994,
   "CurrentFlowrate_l_h" : 0,
   "DosingSinceSetup_ml" : 0,
   "FirmwareVersion" : "2.0207",
   "HardnessIN_CaCO3" : 374,
   "HardnessIN_dH" : 21,
   "HardnessIN_fH" : 37,
   "HardnessIN_mmol_l" : 4,
   "HardnessOUT_CaCO3" : 71,
   "HardnessOUT_dH" : 4,
   "HardnessOUT_fH" : 7,
   "HardnessOUT_mmol_l" : 1,
   "HolidayModeStartTime" : 0,
   "LastRegenerationColumn1" : "2023-11-16 04:42:15",
   "LastRegenerationColumn2" : "2023-11-15 04:41:48",
   "LastServiceCustomer" : "2023-05-18 10:51:07",
   "LastServiceTechnican" : "2021-01-25 13:14:06",
   "OutOfService" : 0,
   "RegenerationCountSinceSetup" : 1505,
   "RegenerationCounterColumn1" : 754,
   "RegenerationCounterColumn2" : 751,
   "RegenerativLevel" : 20,
   "RegenerativRemainingDays" : 26,
   "RegenerativSinceSetup_g" : 245846,
   "ShowError" : 1,
   "WaterSinceSetup_l" : 261633,
   "WaterTreatedCurrentDay_l" : 181,
   "WaterTreatedCurrentMonth_l" : 3137,
   "WaterTreatedCurrentYear_l" : 80700
}
"""


async def test_wrong_code():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=404, body="")
        async with BwtApi("host", "code") as api:
            with pytest.raises(WrongCodeException):
                await api.get_current_data()


async def test_connect_error():
    async with BwtApi("doesntexist", "code") as api:
        with pytest.raises(ConnectException):
            await api.get_current_data()


async def test_unknown_response():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=400, body="")
        async with BwtApi("host", "code") as api:
            with pytest.raises(ApiException):
                await api.get_current_data()


async def test_current_data():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=200, body=current_json)
        async with BwtApi("host", "code") as api:
            result = await api.get_current_data()
            assert result == CurrentResponse(
                errors=[
                    BwtError.REGENERATIV_20,
                    BwtError.MAINTENANCE_CUSTOMER,
                    BwtError.MAINTENANCE_SERVICE,
                ],
                blended_total=318383,
                capacity_1=5485275,
                capacity_2=3833994,
                current_flow=0,
                dosing_total=0,
                firmware_version="2.0207",
                in_hardness=Hardness(caco3=374, dH=21, fH=37, mmol=4),
                out_hardness=Hardness(caco3=71, dH=4, fH=7, mmol=1),
                holiday_mode=0,
                regeneration_last_1="2023-11-16 04:42:15",
                regeneration_last_2="2023-11-15 04:41:48",
                service_customer="2023-05-18 10:51:07",
                service_technician="2021-01-25 13:14:06",
                out_of_service=0,
                regeneration_count_1=754,
                regeneration_count_2=751,
                regeneration_count=1505,
                regenerativ_level=20,
                regenerativ_days=26,
                regenerativ_total=245846,
                show_error=1,
                treated_day=181,
                treated_month=3137,
                treated_year=80700,
            )
