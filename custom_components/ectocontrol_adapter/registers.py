# Register type maping
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
        "name": "Adapter Status",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 10
    },
    REG_R_ADAPTER_VERSION: {
        "name": "Adapter Version",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_R_ADAPTER_UPTIME: {
        "name": "Adapter Uptime",
        "count": 2,
        "data_type": "uint32",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "s",
    },
    REG_R_COOLANT_MIN_TEMP: {
        "name": "Minimum Coolant Temperature",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_R_COOLANT_MAX_TEMP: {
        "name": "Maximum Coolant Temperature",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_R_DHW_MIN_TEMP: {
        "name": "Minimum DHW Temperature",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_R_DHW_MAX_TEMP: {
        "name": "Maximum DHW Temperature",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 60,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_R_COOLANT_TEMP: {
        "name": "Coolant Temperature",
        "count": 1,
        "data_type": "int16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "scale": 0.1
    },
    REG_R_DHW_TEMP: {
        "name": "DHW Temperature",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "scale": 0.1
    },
    REG_R_CURRENT_PRESSURE: {
        "name": "Current Pressure",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "bar",
        "device_class": "pressure",
        "scale": 0.1
    },
    REG_R_CURRENT_VOLUME_FLOW_RATE: {
        "name": "Current Flow Rate",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "L/min",
        "device_class": "volume_flow_rate",
        "scale": 0.1
    },
    REG_R_BURNER_MODULATION: {
        "name": "Burner Modulation",
        "count": 1,
        "data_type": "uint8",
        "input_type": "holding",
        "scan_interval": 5,
        "unit_of_measurement": "%"
    },
    REG_R_BURNER_STATUS: {
        "name": "Burner Status",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 5
    },
    REG_R_ERROR_CODE_MAIN: {
        "name": "Main Error Code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 60
    },
    REG_R_ERROR_CODE_ADD: {
        "name": "Additional Error Code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 60
    },
    REG_R_OUTER_TEMP: {
        "name": "Outer Temperature",
        "count": 1,
        "data_type": "int8",
        "input_type": "holding",
        "scan_interval": 15,
        "unit_of_measurement": "°C",
        "device_class": "temperature"
    },
    REG_R_VENDOR_CODE: {
        "name": "Vendor Code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_R_MODEL_CODE: {
        "name": "Model Code",
        "count": 1,
        "data_type": "uint16",
        "input_type": "holding",
        "scan_interval": 300
    },
    REG_R_OPENTHERM_ERRORS: {
        "name": "OpenTherm Errors",
        "count": 1,
        "data_type": "int8",
        "input_type": "holding",
        "scan_interval": 60
    },
}
