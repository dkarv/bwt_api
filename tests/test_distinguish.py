from datetime import datetime
from zoneinfo import ZoneInfo
import pytest

from bwt_api.api import BwtApi, treated_to_blended
from bwt_api.bwt import BwtModel, determine_bwt_model
from bwt_api.error import BwtError
from bwt_api.data import CurrentResponse, Hardness, BwtStatus

from aioresponses import aioresponses

from bwt_api.exception import ApiException, ConnectException, WrongCodeException

new_json = """
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
   "ShowError" : 2,
   "WaterSinceSetup_l" : 261633,
   "WaterTreatedCurrentDay_l" : 181,
   "WaterTreatedCurrentMonth_l" : 3137,
   "WaterTreatedCurrentYear_l" : 80700
}
"""

silk_json = """{"params":[0,-1,18,23,285,29,16,2,0,9,8,1,8,4,296,158,0,52,2138,9,40,0,100,2275,11,20,50,1,1,0,160,141,20,0,678,1,-1,-1,6,1,1,15,355,-1,-1,-1,-1,0]}"""

async def test_local_api():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api", status=404, body="Not Found")
        result = await determine_bwt_model("host")
        assert result == BwtModel.PERLA_LOCAL_API

async def test_silk():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api", status=404, body="Some other webservice")
        mocked.get("http://host:80/silk/registers", status=200, body=silk_json)
        result = await determine_bwt_model("host")
        assert result == BwtModel.PERLA_SILK
