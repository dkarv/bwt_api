"""Data objects received from the API."""


import enum

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from bwt_api.error import BwtError


class BwtStatus(enum.Enum):
    OK = 0
    WARNING = 1
    ERROR = 2


class SmartDosStatus(enum.IntEnum):
    STANDBY = 2001
    METERING_ACTIVE = 2002
    MINERAL_CONTAINER_LEVEL_LOW = 7001
    MINERAL_CONTAINER_EMPTY = 7002
    SMART_MINERAL_RUNNING_LOW = 7003
    SMART_MINERAL_RUN_OUT = 7004
    AQA_VOLUME_ALARM = 7005
    AQA_WATCH_ALARM = 7006
    AQA_MAXFLOW_ALARM = 7007
    PUMP_FAULT = 8001
    PUMP_POWER_FAULT = 8002
    PUMP_CONTROL_FAULT = 8003

    @classmethod
    def _missing_(cls, value):
        return None


class SubstanceType(enum.IntEnum):
    L1_LE = 1
    L2_L3 = 2
    L4 = 3
    CU2 = 4
    FLUSHING_SOLUTION = 5

    @classmethod
    def _missing_(cls, value):
        return None


@dataclass
class Hardness:
    caco3: int  # ppm CACO3
    dH: int  # dH
    fH: int  # fH
    mmol: int  # mmol / l


@dataclass
class CurrentResponse:
    errors: list[BwtError]
    blended_total: int  # l
    capacity_1: int  # ml * dH
    capacity_2: int  # ml * dH
    current_flow: int  # l / h
    dosing_total: int  # ml
    firmware_version: str
    in_hardness: Hardness
    out_hardness: Hardness
    holiday_mode: int  # -1 or 0: inactive, 1: active, unix timestamp: start in future
    regeneration_last_1: datetime
    regeneration_last_2: datetime
    service_customer: datetime 
    service_technician: datetime
    out_of_service: int
    regeneration_count_1: int
    regeneration_count_2: int
    regeneration_count: int
    regenerativ_level: int  # %
    regenerativ_days: int  # days left
    regenerativ_total: int  # g
    state: BwtStatus
    treated_day: int  # treated water current day
    treated_month: int  # treated water current month
    treated_year: int  # treated water current year
    columns: int # number of columns: 2 for BWT Duo and 1 for BWT Perla One


@dataclass
class DailyResponse:
    # treated water in 30 minute intervals
    # [0] = 00:00 - 00:29
    # [1] = 00:30 - 00:59
    values: list[int]

@dataclass
class MonthlyResponse:
    # treated water in 1 day intervals
    values: list[int]

@dataclass
class YearlyResponse:
    # treated water in 1 month intervals
    values: list[int]


# Smart DOS API Data Classes

@dataclass
class WifiResponse:
    """UUID 0104: Wi-Fi Information"""
    ssid: str  # Wi-Fi network name
    rssi: int  # Wi-Fi signal strength in dBm
    rssiAvg: str  # Average Wi-Fi signal strength in dBm
    rssiSig: str  # Signal strength standard deviation in dBm
    dhcp: bool  # DHCP enabled
    ip: str | None  # IP address
    sn: str | None  # Serial number
    sg: str | None  # Subnet mask
    pDns: str | None  # Primary DNS
    sDns: str | None  # Secondary DNS
    mac: str | None  # MAC address


@dataclass
class DeviceInfoResponse:
    """UUID 0201: Device Information"""
    fw_rev: str  # Firmware Revision
    hw_rev: str  # Hardware Revision
    product_code: str  # Product Code
    uptime: int  # Operating time since last reboot (seconds)
    operating_time: int  # Operating time since first reboot (seconds)
    dev_state: SmartDosStatus | None  # Current device status
    active_states: list[SmartDosStatus | None]  # List of active device statuses
    comm_date: str  # Start-up date (ISO format)
    device_id: str  # Device ID
    device_type: str  # Device type
    device_variant: str  # Device variant
    total_flow: int  # Total treated water in ml
    total_dosed: int  # Total dosed substance in ml

@dataclass
class ConfigurationResponse:
    """UUID 0202: Configuration"""
    buzzer_en: bool  # Buzzer active
    dosing_rate: float  # Metering rate (ml/m³)
    aqa_volume_en: bool  # AQA Volume active
    aqa_watch_en: bool  # AQA Watch active
    aqa_max_flow_en: bool  # AQA MaxFlow active
    aqa_volume_val: float  # AQA Volume value (l)
    volume_per_stroke: float  # Volume per stroke (ml)
    pouch_empty_timeout: int  # Pouch empty timeout (s)
    pouch_not_empty_timeout: int  # Pouch not empty timeout (s)
    aqa_watch_val: int  # AQA Watch value (s)
    aqa_max_flow_val: float  # AQA MaxFlow value (l/h)
    rest_server_en: bool  # REST server active


@dataclass
class TimeResponse:
    """UUID 0208: Time and Timezone"""
    time: int  # Unix timestamp (seconds since 1970-01-01)
    timezone: str  # Timezone string


@dataclass
class PouchInfoResponse:
    """UUID 0401: Pouch/Container Information"""
    tot_cap: float  # Pouch volume (ml)
    exp_date: str  # Substance expiry date (DD.MM.YYYY)
    order_nr: int  # Order number
    batch_nr: int  # Batch number
    substance_type: SubstanceType | None  # Substance type ID
    unit: int  # Unit (0 = ml)


@dataclass
class RemainingCapacityResponse:
    """UUID 0402: Remaining Capacity"""
    rem_capacity: float  # Remaining volume in ml
    rem_capacity_pct: float  # Remaining volume in %
    rem_capacity_days: int  # Remaining volume in days
    unit: int  # Unit (0 = ml)


@dataclass
class TreatedWaterResponse:
    """UUID 0503: Treated Water"""
    total_flow: int  # Total treated water in ml
    total_ticks: int  # Total treated water ticks??


@dataclass
class SubstanceDosageResponse:
    """UUID 0505: Substance Dosage"""
    dosed_mineral: float  # Substance dosage quantity since start-up (ml)
