import enum


class BwtError(enum.Enum):
    OFFLINE_MOTOR_1 = 1
    OFFLINE_MOTOR_2 = 2
    OFFLINE_MOTOR_BLEND = 3
    REGENERATIV_20 = 5
    OVERCURRENT_MOTOR_1 = 8
    OVERCURRENT_MOTOR_2 = 9
    OVERCURRENT_MOTOR_3 = 10
    OVERCURRENT_VALVE = 12
    STOP_VOLUME = 13
    STOP_SENSOR = 14
    CONSTANT_FLOW = 15
    LOW_PRESSURE = 16
    PISTON_POSITION = 21
    ELECTRONIC = 22
    INSUFFICIENT_REGENERATIV = 25
    STOP_WIRELESS_SENSOR = 26
    REGENERATIV_0 = 27
    MAINTENANCE_CUSTOMER = 32
    INSPECTION_CUSTOMER = 33
    MAINTENANCE_SERVICE = 34
    MINERALS_LOW = 35
    MINERALS_0 = 36
    OVERCURRENT_VALVE_1 = 43
    OVERCURRENT_VALVE_2 = 44
    OVERCURRENT_DOSING = 45
    OVERCURRENT_VALVE_BALL = 46
    METER_NOT_COUNTING = 54
    REGENERATION_DRAIN = 55
    INIT_PCB_0 = 56
    INIT_PCB_1 = 57
    POSITION_MOTOR_1 = 58
    POSITION_MOTOR_2 = 59
    CONDUCTIVITY_HIGH = 61
    CONDUCTIVITY_LIMIT_1 = 62
    CONDUCTIVITY_LIMIT_2 = 63
    CONDUCTIVITY_LIMIT_WATER = 64
    NO_FUNCTION = 65
    TEMPERATURE_DISCONNECTED = 66
    TEMPERATURE_HIGH = 67
    OFFLINE_VALVE_BALL = 68
    EXTERNAL_FILTER_CHANGE = 74
    BRINE_UNSATURATED = 75
    DOSING_FAULT = 88

    def is_fatal(self) -> bool:
        return self not in WARNING_CODES


WARNING_CODES = [
    BwtError.REGENERATIV_20,
    BwtError.CONSTANT_FLOW,
    BwtError.LOW_PRESSURE,
    BwtError.INSUFFICIENT_REGENERATIV,
    BwtError.MAINTENANCE_CUSTOMER,
    BwtError.INSPECTION_CUSTOMER,
    BwtError.MAINTENANCE_SERVICE,
    BwtError.MINERALS_LOW,
    BwtError.MINERALS_0,
    BwtError.METER_NOT_COUNTING,
    BwtError.REGENERATION_DRAIN,
    BwtError.CONDUCTIVITY_HIGH,
    BwtError.CONDUCTIVITY_LIMIT_1,
    BwtError.CONDUCTIVITY_LIMIT_2,
    BwtError.CONDUCTIVITY_LIMIT_WATER,
    BwtError.TEMPERATURE_DISCONNECTED,
    BwtError.TEMPERATURE_HIGH,
    BwtError.EXTERNAL_FILTER_CHANGE,
    BwtError.BRINE_UNSATURATED,
    BwtError.DOSING_FAULT,
]