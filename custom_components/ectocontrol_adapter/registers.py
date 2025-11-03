from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
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

# State register offset
REG_STATE_OFFSET = 0x30

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
REGISTERS = {
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
                "category": EntityCategory.DIAGNOSTIC
            },
            0x0700: {
                "type": BM_VALUE,
                "name": "adapter_bus",
                "device_class": SensorDeviceClass.ENUM,
                "choices": {
                    0b00000000000: "Opentherm",
                    0b00100000000: "eBus",
                    0b01000000000: "Navien"
                }
            },
            0x0800: {
                "type": BM_BINARY,
                "name": "сonnectivity",
                "device_class": BinarySensorDeviceClass.CONNECTIVITY
            }
        }
    },
    REG_R_ADAPTER_VERSION: {
        "name": "adapter_version",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300,
        "category": EntityCategory.DIAGNOSTIC
    },
    REG_R_ADAPTER_UPTIME: {
        "name": "adapter_uptime",
        "count": 2,
        "data_type": "uint32",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "s",
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
        "device_class": SensorDeviceClass.TEMPERATURE
    },
    REG_R_COOLANT_MAX_TEMP: {
        "name": "coolant_max_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE
    },
    REG_R_DHW_MIN_TEMP: {
        "name": "dhw_min_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE
    },
    REG_R_DHW_MAX_TEMP: {
        "name": "dhw_max_temp",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE
    },
    REG_R_COOLANT_TEMP: {
        "name": "coolant_temp",
        "count": 1,
        "data_type": "int16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.1
    },
    REG_R_DHW_TEMP: {
        "name": "dhw_temp",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "scale": 0.1
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
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            0b010: {
                "type": BM_BINARY,
                "name": "burner_heating",
                "device_class": BinarySensorDeviceClass.RUNNING
            },
            0b100: {
                "type": BM_BINARY,
                "name": "burner_dhw",
                "device_class": BinarySensorDeviceClass.RUNNING
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
        "device_class": SensorDeviceClass.TEMPERATURE
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
        "data_type": "int8",
        "input_type": "holding",
        "scan_interval": 60
    },
}
