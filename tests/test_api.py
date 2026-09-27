from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import Mock
from pathlib import Path
import pytest
from aiohttp.client_reqrep import ClientResponse

from bwt_api.api import BwtApi, BwtSmartDosApi, BwtSilkApi, treated_to_blended
from bwt_api.error import BwtError
from bwt_api.data import CurrentResponse, Hardness, BwtStatus, SmartDosStatus, SubstanceType

from aioresponses import aioresponses

# Compatibility shim for aioresponses with aiohttp 3.14+.
_original_client_response_init = ClientResponse.__init__

def _compat_client_response_init(self, method, url, *args, stream_writer=None, **kwargs):
    if stream_writer is None:
        stream_writer = Mock(output_size=0)
    return _original_client_response_init(self, method, url, *args, stream_writer=stream_writer, **kwargs)

ClientResponse.__init__ = _compat_client_response_init

from bwt_api.exception import ApiException, ConnectException, WrongCodeException

__author__ = "dkarv"
__copyright__ = "dkarv"
__license__ = "MIT"


current_json = """
{
   "ActiveErrorIDs" : "5,32,34,29",
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

current_json_empty_errors = """
{
   "ActiveErrorIDs" : "",
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
   "ShowError" : 0,
   "WaterSinceSetup_l" : 261633,
   "WaterTreatedCurrentDay_l" : 181,
   "WaterTreatedCurrentMonth_l" : 3137,
   "WaterTreatedCurrentYear_l" : 80700
}
"""


def load_json_str(name: str) -> str:
    """Load a JSON file from tests/data/smartdos and return its text."""
    return (Path(__file__).parent / "data" / "smartdos" / name).read_text()

current_json_perla_one = """
{
   "ActiveErrorIDs" : "",
   "BlendedWaterSinceSetup_l" : 189985,
   "CapacityColumn1_ml_dH" : 4487511,
   "CapacityColumn2_ml_dH" : -1,
   "CurrentFlowrate_l_h" : 0,
   "DosingSinceSetup_ml" : 0,
   "FirmwareVersion" : "2.0211",
   "HardnessIN_CaCO3" : 409,
   "HardnessIN_dH" : 23,
   "HardnessIN_fH" : 41,
   "HardnessIN_mmol_l" : 4,
   "HardnessOUT_CaCO3" : 107,
   "HardnessOUT_dH" : 6,
   "HardnessOUT_fH" : 11,
   "HardnessOUT_mmol_l" : 1,
   "HolidayModeStartTime" : 0,
   "LastRegenerationColumn1" : "2025-01-15 03:00:15",
   "LastRegenerationColumn2" : "1970-01-01 00:59:59",
   "LastServiceCustomer" : "2024-11-25 09:13:48",
   "LastServiceTechnican" : "2023-08-07 11:13:51",
   "OutOfService" : 0,
   "RegenerationCountSinceSetup" : 692,
   "RegenerationCounterColumn1" : 692,
   "RegenerationCounterColumn2" : 0,
   "RegenerativLevel" : 37,
   "RegenerativRemainingDays" : 62,
   "RegenerativSinceSetup_g" : 207305,
   "ShowError" : 0,
   "WaterSinceSetup_l" : 148544,
   "WaterTreatedCurrentDay_l" : 179,
   "WaterTreatedCurrentMonth_l" : 514,
   "WaterTreatedCurrentYear_l" : 500
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


async def test_timeout_error():
    """Timeouts should be wrapped as ConnectException, not escape as raw TimeoutError."""
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", exception=TimeoutError())
        async with BwtApi("host", "code") as api:
            with pytest.raises(ConnectException):
                await api.get_current_data()


async def test_unknown_response():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=400, body="")
        async with BwtApi("host", "code") as api:
            with pytest.raises(ApiException):
                await api.get_current_data()


async def test_invalid_json_response():
    """HTTP 200 with non-JSON body should raise ApiException, not JSONDecodeError."""
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=200, body="not json")
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
                    BwtError(29),
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
                regeneration_last_1=datetime(2023, 11, 16, 4, 42,15,0),
                regeneration_last_2=datetime(2023, 11, 15, 4, 41,48,0),
                service_customer=datetime(2023, 5, 18, 10, 51,7,0),
                service_technician=datetime(2021, 1, 25, 13, 14,6,0),
                out_of_service=0,
                regeneration_count_1=754,
                regeneration_count_2=751,
                regeneration_count=1505,
                regenerativ_level=20,
                regenerativ_days=26,
                regenerativ_total=245846,
                state=BwtStatus.ERROR,
                treated_day=181,
                treated_month=3137,
                treated_year=80700,
                columns=2,
            )


async def test_empty_errors():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=200, body=current_json_empty_errors)
        async with BwtApi("host", "code") as api:
            result = await api.get_current_data()
            assert result == CurrentResponse(
                errors=[],
                blended_total=318383,
                capacity_1=5485275,
                capacity_2=3833994,
                current_flow=0,
                dosing_total=0,
                firmware_version="2.0207",
                in_hardness=Hardness(caco3=374, dH=21, fH=37, mmol=4),
                out_hardness=Hardness(caco3=71, dH=4, fH=7, mmol=1),
                holiday_mode=0,
                regeneration_last_1=datetime(2023, 11, 16, 4, 42,15,0),
                regeneration_last_2=datetime(2023, 11, 15, 4, 41,48,0),
                service_customer=datetime(2023, 5, 18, 10, 51,7,0),
                service_technician=datetime(2021, 1, 25, 13, 14,6,0),
                out_of_service=0,
                regeneration_count_1=754,
                regeneration_count_2=751,
                regeneration_count=1505,
                regenerativ_level=20,
                regenerativ_days=26,
                regenerativ_total=245846,
                state=BwtStatus.OK,
                treated_day=181,
                treated_month=3137,
                treated_year=80700,
                columns=2,
            )


async def test_perla_one():
    with aioresponses() as mocked:
        mocked.get("http://host:8080/api/GetCurrentData", status=200, body=current_json_perla_one)
        async with BwtApi("host", "code") as api:
            result = await api.get_current_data()
            assert result == CurrentResponse(
                errors=[],
                blended_total=189985,
                capacity_1=4487511,
                capacity_2=-1,
                current_flow=0,
                dosing_total=0,
                firmware_version="2.0211",
                in_hardness=Hardness(caco3=409, dH=23, fH=41, mmol=4),
                out_hardness=Hardness(caco3=107, dH=6, fH=11, mmol=1),
                holiday_mode=0,
                regeneration_last_1=datetime(2025, 1, 15, 3, 0, 15, 0),
                regeneration_last_2=datetime(1970, 1, 1, 0, 59, 59, 0),
                service_customer=datetime(2024, 11, 25, 9, 13, 48, 0),
                service_technician=datetime(2023, 8, 7, 11, 13, 51, 0),
                out_of_service=0,
                regeneration_count_1=692,
                regeneration_count_2=0,
                regeneration_count=692,
                regenerativ_level=37,
                regenerativ_days=62,
                regenerativ_total=207305,
                state=BwtStatus.OK,
                treated_day=179,
                treated_month=514,
                treated_year=500,
                columns=1,
            )

def test_unknown_error_no_mutation():
    """Unknown error codes must not mutate the UNKNOWN singleton."""
    err1 = BwtError(29)
    assert err1.value == 29
    assert err1.name == "UNKNOWN_29"
    err2 = BwtError(123)
    assert err2.value == 123
    assert err2.name == "UNKNOWN_123"
    # UNKNOWN singleton must be untouched
    assert BwtError.UNKNOWN.value == -1
    # Different unknown codes produce different instances
    assert err1 is not err2

async def test_smartdos_get_wifi_info():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0104",
            status=200,
                body=load_json_str("gatt_0104.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_wifi_info()
            assert result.ssid == "MyWiFi"
            assert result.rssiAvg == "-54.00"
            assert result.mac == "AA:BB:CC:DD:EE:FF"


async def test_smartdos_get_gatt_0201():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0201",
            status=200,
                body=load_json_str("gatt_0201.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_gatt_0201()
            assert result["fwRev"] == "1.2.0"
            assert result["productCode"] == "1AAA-2BBB"


async def test_smartdos_unknown_response():
    with aioresponses() as mocked:
        mocked.get("http://host:80/api/v1/gatt/0201", status=404, body="Not Found")
        async with BwtSmartDosApi("host") as api:
            with pytest.raises(ApiException):
                await api.get_gatt_0201()


async def test_smartdos_get_configuration():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0202",
            status=200,
                body=load_json_str("gatt_0202.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_configuration()
            assert result.buzzer_en is False
            assert result.dosing_rate == 10
            assert result.rest_server_en is True


async def test_smartdos_get_time_info():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0208",
            status=200,
                body=load_json_str("gatt_0208.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_time_info()
            assert result.time == "2026-07-14 12:00:00"
            assert result.timezone == "UTC"


async def test_smartdos_device_info_parses_status_values():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0201",
            status=200,
            body='{"fwRev":"1.2.0","hwRev":"2.4.0(A)","productCode":"3HZR-1R37","iotDevId":"5b29b9e9-24c5-4eea-a599-927922a89f5a","iotDevType":"bwt_bewados","iotDevVariant":"dev","uptime":6510811,"operatingTime":40773211,"devState":2001,"activeStates":[2001],"commDate":"2026-01-04T10:01:05.891Z","lifeTimeFlow_ml":112507432,"lifeTimeDosed_ml":2746.1572265625}',
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_device_info()
            assert result.dev_state == SmartDosStatus.STANDBY
            assert result.active_states == [SmartDosStatus.STANDBY]


async def test_smartdos_get_remaining_capacity():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0402",
            status=200,
                body=load_json_str("gatt_0402.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_remaining_capacity()
            assert 1 in result
            assert result[1].rem_capacity == 1451.1103515625
            assert result[1].rem_capacity_pct == 97


async def test_smartdos_get_treated_water():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0503",
            status=200,
                body=load_json_str("gatt_0503.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_treated_water()
            assert 1 in result
            assert result[1].total_flow == 112507432
            assert 2 in result
            assert result[2].total_flow == 20244130


async def test_smartdos_get_substance_dosage():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0505",
            status=200,
                body=load_json_str("gatt_0505.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_substance_dosage()
            assert result.dosed_mineral == 2746.1572265625


async def test_smartdos_pouch_info_parses_substance_type():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/api/v1/gatt/0401",
            status=200,
                body=load_json_str("gatt_0401.json"),
            headers={"Content-Type": "application/json"},
        )
        async with BwtSmartDosApi("host") as api:
            result = await api.get_pouch_info()
            assert result.substance_type == SubstanceType.L1_LE
            assert result.tot_cap == 1000

def test_treated_to_blended():
    assert treated_to_blended(0, 21, 4) == 0
    assert treated_to_blended(100, 21, 21) == 100
    assert treated_to_blended(10, 20, 4) == 12.5
    assert treated_to_blended(306, 21, 4) == 378
    assert treated_to_blended(191, 21, 4) == pytest.approx(235.9411)
    # Edge case: hardness_in == 0 should return treated as-is, not divide by zero
    assert treated_to_blended(100, 0, 0) == 100


async def test_silk_get_registers():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/silk/registers",
            status=200,
            body='{"params":[0, -1, 8, 30, 250]}',
            headers={"Content-Type": "application/json"},
        )
        async with BwtSilkApi("host") as api:
            result = await api.get_registers()
            assert result == [0, -1, 8, 30, 250]


async def test_silk_get_status():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/silk/status",
            status=200,
            body='{"version":"2.3.7","gitver":1234,"productCode":"SILK"}',
            headers={"Content-Type": "application/json"},
        )
        async with BwtSilkApi("host") as api:
            result = await api.get_status()
            assert result["version"] == "2.3.7"
            assert result["gitver"] == 1234
            assert result["productCode"] == "SILK"


async def test_silk_get_status_error():
    with aioresponses() as mocked:
        mocked.get(
            "http://host:80/silk/status",
            status=500,
            body="boom",
            headers={"Content-Type": "text/plain"},
        )
        async with BwtSilkApi("host") as api:
            with pytest.raises(ApiException):
                await api.get_status()
