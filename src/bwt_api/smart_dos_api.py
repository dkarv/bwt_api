"""The BWT Smart Dos API class."""

import aiohttp
import logging
from typing import Any

from bwt_api.data import (
    WifiResponse,
    DeviceInfoResponse,
    SmartDosStatus,
    SubstanceType,
    ConfigurationResponse,
    TimeResponse,
    PouchInfoResponse,
    RemainingCapacityResponse,
    TreatedWaterResponse,
    SubstanceDosageResponse,
)
from bwt_api.exception import ApiException, ConnectException

_logger = logging.getLogger(__name__)


class BwtSmartDosApi:
    """BWT Smart Dos Api."""
    _session: aiohttp.ClientSession
    _host: str

    def __init__(self, host: str):
        self._host = host
        self._session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *err):
        await self.close()

    async def close(self):
        await self._session.close()

    async def _get_gatt(self, uuid: str) -> dict[str, Any]:
        """Internal method to fetch GATT characteristic JSON."""
        try:
            async with self._session.get(f"http://{self._host}:80/api/v1/gatt/{uuid}") as response:
                _logger.debug(
                    f"Response status: {response.status}, content-type: {response.headers['content-type']}"
                )
                if response.status == 200:
                    json = await response.json(content_type=None)
                    _logger.debug(f"Raw response for UUID {uuid}: {json}")
                    return json
                text = await response.text()
                _logger.warning(f"Unknown response with status {response.status}: {text}")
                raise ApiException(f"Unknown response: {text}")
        except aiohttp.ClientConnectorError as e:
            raise ConnectException from e

    async def get_wifi_info(self) -> WifiResponse:
        """UUID 0104: Get Wi-Fi name and signal strength."""
        _logger.debug(f"Fetching Wi-Fi info from {self._host}")
        raw = await self._get_gatt("0104")
        return WifiResponse(ssid=raw["ssid"], rssi=raw["rssi"])

    async def get_device_info(self) -> DeviceInfoResponse:
        """UUID 0201: Get device information."""
        _logger.debug(f"Fetching device info from {self._host}")
        raw = await self._get_gatt("0201")
        return DeviceInfoResponse(
            fw_rev=raw["fwRev"],
            hw_rev=raw["hwRev"],
            product_code=raw["productCode"],
            uptime=raw["uptime"],
            operating_time=raw["operatingTime"],
            dev_state=SmartDosStatus(raw["devState"]),
            active_states=[SmartDosStatus(state) for state in raw["activeStates"]],
            comm_date=raw["commDate"],
        )

    async def get_configuration(self) -> ConfigurationResponse:
        """UUID 0202: Get device configuration."""
        _logger.debug(f"Fetching configuration from {self._host}")
        raw = await self._get_gatt("0202")
        return ConfigurationResponse(
            buzzer_en=raw["buzzerEn"],
            dosing_rate=raw["dosingRate"],
            aqa_volume_en=raw["aqaVolumeEn"],
            aqa_watch_en=raw["aqaWatchEn"],
            aqa_max_flow_en=raw["aqaMaxFlowEn"],
            aqa_volume_val=raw["aqaVolumeVal"],
        )

    async def get_time_info(self) -> TimeResponse:
        """UUID 0208: Get time and timezone information."""
        _logger.debug(f"Fetching time info from {self._host}")
        raw = await self._get_gatt("0208")
        return TimeResponse(time=raw["time"], timezone=raw["timezone"])

    async def get_pouch_info(self) -> PouchInfoResponse:
        """UUID 0401: Get pouch/container information."""
        _logger.debug(f"Fetching pouch info from {self._host}")
        raw = await self._get_gatt("0401")
        return PouchInfoResponse(
            tot_cap=raw["totCap"],
            exp_date=raw["expDate"],
            order_nr=raw["orderNr"],
            batch_nr=raw["batchNr"],
            substance_type=SubstanceType(raw["id"]),
            unit=raw["unit"],
        )

    async def get_remaining_capacity(self) -> RemainingCapacityResponse:
        """UUID 0402: Get remaining capacity information."""
        _logger.debug(f"Fetching remaining capacity from {self._host}")
        raw = await self._get_gatt("0402")
        return RemainingCapacityResponse(
            rem_capacity=raw["remCapacity"],
            rem_capacity_pct=raw["remCapacityPct"],
            rem_capacity_days=raw["remCapacityDays"],
        )

    async def get_treated_water(self) -> TreatedWaterResponse:
        """UUID 0503: Get treated water information."""
        _logger.debug(f"Fetching treated water from {self._host}")
        raw = await self._get_gatt("0503")
        total_flow = raw["flow"]["1"]["totFlow"]
        return TreatedWaterResponse(total_flow=total_flow)

    async def get_substance_dosage(self) -> SubstanceDosageResponse:
        """UUID 0505: Get substance dosage information."""
        _logger.debug(f"Fetching substance dosage from {self._host}")
        raw = await self._get_gatt("0505")
        return SubstanceDosageResponse(dosed_mineral=raw["dosedMineral"])

    async def get_gatt_0201(self) -> dict[str, Any]:
        """Fetch the Smart Dos GATT 0201 characteristic JSON (raw)."""
        return await self._get_gatt("0201")
