# Reading registers of the ectoControl adapter
REG_ADAPTER_STATUS = 0x0010
REG_ADAPTER_VERSION = 0x0011
REG_ADAPTER_UPTIME = 0x0012
REG_COOLANT_MIN_TEMP = 0x0014
REG_COOLANT_MAX_TEMP = 0x0015
REG_DHW_MIN_TEMP = 0x0016
REG_DHW_MAX_TEMP = 0x0017
REG_COOLANT_TEMP = 0x0018
REG_DHW_TEMP = 0x0019
REG_CURRENT_PRESSURE = 0x001A
REG_CURRENT_VOLUME_FLOW_RATE = 0x001B
REG_BURNER_MODULATION = 0x001C
REG_BURNER_STATUS = 0x001D
REG_ERROR_CODE_MAIN = 0x001E
REG_ERROR_CODE_ADD = 0x001F
REG_OUTER_TEMP = 0x0020
REG_VENDOR_CODE = 0x0021
REG_MODEL_CODE = 0x0022
REG_OPENTHERM_ERRORS = 0x0023

# Data types for unpack via python `struct` module
REGISTERS = {
    REG_ADAPTER_STATUS: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 10
    },
    REG_ADAPTER_VERSION: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_ADAPTER_UPTIME: {
        "count": 2,
        "data_type": "I",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "s",
    },
    REG_COOLANT_MIN_TEMP: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_COOLANT_MAX_TEMP: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_DHW_MIN_TEMP: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_DHW_MAX_TEMP: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_COOLANT_TEMP: {
        "count": 1,
        "data_type": "h",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "scale": 0.1
    },
    REG_DHW_TEMP: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "scale": 0.1
    },
    REG_CURRENT_PRESSURE: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "bar",
        "device_class": "pressure",
        "scale": 0.1
    },
    REG_CURRENT_VOLUME_FLOW_RATE: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "L/min",
        "device_class": "volume_flow_rate",
        "scale": 0.1
    },
    REG_BURNER_MODULATION: {
        "count": 1,
        "data_type": "B",
        "input_type": "holding",
        "scan_interval": 5,
        "unit_of_measurement": "%"
    },
    REG_BURNER_STATUS: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 5
    },

    REG_ERROR_CODE_MAIN: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 60
    },
    REG_ERROR_CODE_ADD: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 60
    },
    REG_OUTER_TEMP: {
        "count": 1,
        "data_type": "b",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_VENDOR_CODE: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_MODEL_CODE: {
        "count": 1,
        "data_type": "H",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_OPENTHERM_ERRORS: {
        "count": 1,
        "data_type": "b",
        "input_type": "holding",
        "scan_interval": 60
    },
}
