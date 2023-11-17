"""Data objects received from the API."""


from dataclasses import dataclass
from bwt_api.error import BwtError


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
    regeneration_last_1: str  # date time
    regeneration_last_2: str  # date time
    service_customer: str
    service_technician: str
    out_of_service: int
    regeneration_count_1: int
    regeneration_count_2: int
    regeneration_count: int
    regenerativ_level: int  # %
    regenerativ_days: int  # days left
    regenerativ_total: int  # g
    show_error: int  # 0: ok/blue, 1: warning/yellow, 2: error/red
    treated_day: int  # treated water current day
    treated_month: int  # treated water current month
    treated_year: int  # treated water current year


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