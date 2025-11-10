from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.helpers.entity import EntityCategory

from .converters import uptime_to_boottime


# Register type maping for struct python module
REG_TYPE_MAPPING = {
    # 8-bit types (single byte)
    'uint8': 'B',
    'int8': 'b',

    # 16-bit types (single register)
    'uint16': 'H',
    'int16': 'h',

    # 32-bit types (two registers)
    'uint32': 'I',
    'int32': 'i',
    'float32': 'f',

    # 64-bit types (four registers)
    'uint64': 'Q',
    'int64': 'q',
    'float64': 'd',
}

# Bitmasks value types
BM_VALUE = 1
BM_BINARY = 2

# One byte types
BYTE_TYPES = ['int8', 'uint8']

# Default scan interval
REG_DEFAULT_SCAN_INTERVAL = 15

# Default max write retries
REG_DEFAULT_MAX_RETRIES = 3

# Default retry delay (float, seconds)
REG_DEFAULT_RETRY_DELAY = 0.3

# Default step for numbers
REG_DEFAULT_NUMBER_STEP = 1.0

# Status register offset
REG_STATUS_OFFSET = 0x30

# Status values
REG_STATUS_ERROR_OP = -2  # boiler read/write error
REG_STATUS_UNSUPPORTED = -1
REG_STATUS_OK = 0
REG_STATUS_NOT_INIT = 1

# Reading registers of the ectoControl adapter
REG_R_ADAPTER_STATUS = 0x0010
REG_R_ADAPTER_VERSION = 0x0011
REG_R_ADAPTER_UPTIME = 0x0012
REG_R_COOLANT_MIN_TEMP = 0x0014
REG_R_COOLANT_MAX_TEMP = 0x0015
REG_R_DHW_MIN_TEMP = 0x0016
REG_R_DHW_MAX_TEMP = 0x0017
REG_R_COOLANT_TEMP = 0x0018
REG_R_DHW_TEMP = 0x0019
REG_R_CURRENT_PRESSURE = 0x001A
REG_R_CURRENT_VOLUME_FLOW_RATE = 0x001B
REG_R_BURNER_MODULATION = 0x001C
REG_R_BURNER_STATUS = 0x001D
REG_R_ERROR_CODE_MAIN = 0x001E
REG_R_ERROR_CODE_ADD = 0x001F
REG_R_OUTER_TEMP = 0x0020
REG_R_VENDOR_CODE = 0x0021
REG_R_MODEL_CODE = 0x0022
REG_R_OPENTHERM_ERRORS = 0x0023

# Writing registers of the ectoControl adapter
REG_W_CONNECT_TYPE = 0x0030
REG_W_COOLANT_TEMP = 0x0031
REG_W_COOLANT_EMERGENCY_TEMP = 0x0032
REG_W_COOLANT_MIN_TEMP = 0x0033
REG_W_COOLANT_MAX_TEMP = 0x0034
REG_W_DHW_MIN_TEMP = 0x0035
REG_W_DHW_MAX_TEMP = 0x0036
REG_W_DHW_TEMP = 0x0037
REG_W_BURNER_MODULATION = 0x0038
REG_W_MODE = 0x0039

# Command registers
REG_W_COMMAND = 0x0080
REG_R_COMMAND_REPLY = 0x0081

# Data types for unpack via python `struct` module
REGISTERS_R = {
    REG_R_ADAPTER_STATUS: {
        "name": "adapter_status_raw",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 10,
        "category": EntityCategory.DIAGNOSTIC,
        "bitmasks": {
            0x00FF: {
                "type": BM_VALUE,
                "name": "last_reboot_code",
                "category": EntityCategory.DIAGNOSTIC,
                "icon": "mdi:code-braces-box"
            },
            0x0700: {
                "type": BM_VALUE,
                "name": "adapter_bus",
                "device_class": SensorDeviceClass.ENUM,
                "choices": {
                    0b00000000000: "Opentherm",
                    0b00100000000: "eBus",
                    0b01000000000: "Navien"
                },
                "icon": "mdi:alphabetical-variant"
            },
            0x0800: {
                "type": BM_BINARY,
                "name": "сonnectivity",
                "device_class": BinarySensorDeviceClass.CONNECTIVITY
            }
        }
    },
    REG_R_ADAPTER_VERSION: {
        "name": "adapter_version_raw",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300,
        "category": EntityCategory.DIAGNOSTIC,
        "bitmasks": {
            0x00FF: {
                "type": BM_VALUE,
                "name": "adapter_sw_version",
                "category": EntityCategory.DIAGNOSTIC,
                "icon": "mdi:github"
            },
            0xFF00: {
                "rshift": 8,
                "type": BM_VALUE,
                "name": "adapter_hw_version",
                "category": EntityCategory.DIAGNOSTIC,
                "icon": "mdi:chip"
            }
        }
    },
    REG_R_ADAPTER_UPTIME: {
        "name": "adapter_uptime",
        "count": 2,
        "data_type": "uint32",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "s",
        "device_class": SensorDeviceClass.DURATION,
        "category": EntityCategory.DIAGNOSTIC,
        "converters": {
            "uptime_to_boottime": {
                "converter": uptime_to_boottime,
                "name": "adapter_boot_time",
                "device_class": SensorDeviceClass.TIMESTAMP
            }
        }
    },
    REG_R_COOLANT_MIN_TEMP: {
        "name": "coolant_min_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_COOLANT_MAX_TEMP: {
        "name": "coolant_max_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_DHW_MIN_TEMP: {
        "name": "dhw_min_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_DHW_MAX_TEMP: {
        "name": "dhw_max_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_COOLANT_TEMP: {
        "name": "coolant_temp",
        "count": 1,
        "data_type": "int16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.1,
        "icon": "mdi:coolant-temperature"
    },
    REG_R_DHW_TEMP: {
        "name": "dhw_temp",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.1,
        "icon": "mdi:thermometer-water"
    },
    REG_R_CURRENT_PRESSURE: {
        "name": "current_pressure",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "bar",
        "device_class": SensorDeviceClass.PRESSURE,
        "scale": 0.1
    },
    REG_R_CURRENT_VOLUME_FLOW_RATE: {
        "name": "current_flow_rate",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "L/min",
        "device_class": SensorDeviceClass.VOLUME_FLOW_RATE,
        "scale": 0.1
    },
    REG_R_BURNER_MODULATION: {
        "name": "burner_modulation",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 5,
        "unit_of_measurement": "%",
        "device_class": SensorDeviceClass.POWER_FACTOR
    },
    REG_R_BURNER_STATUS: {
        "name": "burner_status_raw",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 5,
        "category": EntityCategory.DIAGNOSTIC,
        "bitmasks": {
            0b001: {
                "type": BM_BINARY,
                "name": "burner_status",
                "device_class": BinarySensorDeviceClass.RUNNING,
                "icon": "mdi:fire"
            },
            0b010: {
                "type": BM_BINARY,
                "name": "burner_heating",
                "device_class": BinarySensorDeviceClass.RUNNING,
                "icon": "mdi:heating-coil"
            },
            0b100: {
                "type": BM_BINARY,
                "name": "burner_dhw",
                "device_class": BinarySensorDeviceClass.RUNNING,
                "icon": "mdi:faucet"
            }
        }
    },
    REG_R_ERROR_CODE_MAIN: {
        "name": "main_error_code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 60,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_ERROR_CODE_ADD: {
        "name": "add_error_code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 60,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_OUTER_TEMP: {
        "name": "outer_temp",
        "count": 1,
        "data_type": "int8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "icon": "mdi:home-thermometer"
    },
    REG_R_VENDOR_CODE: {
        "name": "vendor_code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_MODEL_CODE: {
        "name": "model_code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_OPENTHERM_ERRORS: {
        "name": "opentherm_errors",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "category": EntityCategory.DIAGNOSTIC,
        "bitmasks": {
            0x0001: {
                "type": BM_BINARY,
                "name": "opentherm_maintenance_required",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0002: {
                "type": BM_BINARY,
                "name": "opentherm_boiler_blocked",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0004: {
                "type": BM_BINARY,
                "name": "opentherm_low_pressure",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0008: {
                "type": BM_BINARY,
                "name": "opentherm_ignition_error",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0010: {
                "type": BM_BINARY,
                "name": "opentherm_low_air_pressure",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0020: {
                "type": BM_BINARY,
                "name": "opentherm_coolant_overheating",
                "device_class": BinarySensorDeviceClass.PROBLEM,
                "category": EntityCategory.DIAGNOSTIC
            }
        }
    }
}

# Input types
NUMBER_INPUT = "number"
SWITCH_INPUT = "switch"

REGISTERS_W = {
    REG_W_CONNECT_TYPE: {
        "name": "connect_type",
        "on_value": 1,
        "off_value": 0,
        "input_type": SWITCH_INPUT,
        "icon": "mdi:alarm-panel-outline",
        "device_class": SwitchDeviceClass.SWITCH
    },
    REG_W_COOLANT_TEMP: {
        "name": "coolant_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 40,
        "step": 1,
        "scale": 10,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:coolant-temperature",
        "device_class": NumberDeviceClass.TEMPERATURE
    },
    REG_W_COOLANT_EMERGENCY_TEMP: {
        "name": "coolant_emergency_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 40,
        "step": 1,
        "scale": 10,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-alert",
        "device_class": NumberDeviceClass.TEMPERATURE
    },
    REG_W_COOLANT_MIN_TEMP: {
        "name": "coolant_min_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 40,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-minus",
        "device_class": NumberDeviceClass.TEMPERATURE,
        "category": EntityCategory.CONFIG
    },
    REG_W_COOLANT_MAX_TEMP: {
        "name": "coolant_max_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 80,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-plus",
        "device_class": NumberDeviceClass.TEMPERATURE,
        "category": EntityCategory.CONFIG
    },
    REG_W_DHW_MIN_TEMP: {
        "name": "dhw_min_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 40,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-minus",
        "device_class": NumberDeviceClass.TEMPERATURE,
        "category": EntityCategory.CONFIG
    },
    REG_W_DHW_MAX_TEMP: {
        "name": "dhw_max_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 55,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-plus",
        "device_class": NumberDeviceClass.TEMPERATURE,
        "category": EntityCategory.CONFIG
    },
    REG_W_DHW_TEMP: {
        "name": "dhw_temp",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 40,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "°C",
        "icon": "mdi:thermometer-water",
        "device_class": NumberDeviceClass.TEMPERATURE
    },
    REG_W_BURNER_MODULATION: {
        "name": "burner_modulation",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 0,
        "step": 1,
        "input_type": NUMBER_INPUT,
        "unit_of_measurement": "%",
        "icon": "mdi:gas-burner",
        "device_class": NumberDeviceClass.POWER_FACTOR
    },
}
