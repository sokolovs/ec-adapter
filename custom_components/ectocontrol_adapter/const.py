# EC domain
DOMAIN = "ectocontrol_adapter"
SENSOR_UPDATE_SIGNAL = "EC_ADAPTER_OPTIONS_UPDATED"

# Timout for Modbus response
DEFAULT_RESPONSE_TIMEOUT = 5

# Default slave/unit ID
DEFAULT_SLAVE_ID = 1

# Modbus type choices
DEFAULT_MODBUS_TYPE = "tcp"
MODBUS_TYPES = {
    "tcp": "TCP",
    "udp": "UDP",
    "rtuovertcp": "RTU over TCP",
    "serial": "Serial"
}

# Baud rate choices
DEFAULT_SERIAL_BAUDRATE = 19200
SERIAL_BAUDRATES = (
    300,
    600,
    1200,
    2400,
    4800,
    9600,
    14400,
    19200,
    28800,
    38400,
    57600,
    115200,
    230400,
    460800,
    921600
)

# Byte size (data bits) choices
DEFAULT_SERIAL_BYTESIZE = 8
SERIAL_BYTESIZES = (8, 7, 6, 5)

# Parity choices
DEFAULT_PARITY = "N"
SERIAL_PARITIES = {
    "N": "None",
    "E": "Even",
    "O": "Odd"
}

# Stop bits
DEFAULT_STOPBITS = 1
SERIAL_STOPBITS = (1, 2)
