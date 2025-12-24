from awesomeversion import AwesomeVersion

from homeassistant.const import __version__ as HAVERSION  # noqa: N812

HA_VERSION = AwesomeVersion(HAVERSION)

# EC domain
DOMAIN = "ectocontrol_adapter"
SENSOR_UPDATE_SIGNAL = "EC_ADAPTER_OPTIONS_UPDATED"

# Config options
OPT_NAME = "name"
OPT_RESPONSE_TIMEOUT = "response_timeout"
OPT_MODBUS_TYPE = "modbus_type"
OPT_SLAVE = "slave"
OPT_DEVICE = "device"
OPT_BAUDRATE = "baudrate"
OPT_BYTESIZE = "bytesize"
OPT_PARITY = "parity"
OPT_STOPBITS = "stopbits"
OPT_HOST = "host"
OPT_PORT = "port"

# Default timeout for Modbus response
DEFAULT_RESPONSE_TIMEOUT = 5

# Default slave/unit ID
DEFAULT_SLAVE_ID = 1

# Default serial port
DEFAULT_DEVICE = "/dev/ttyUSB0"

# Default TCP/UDP port
DEFAULT_PORT = 502

# Modbus type choices
MODBUS_TYPE_TCP = "tcp"
MODBUS_TYPE_UDP = "udp"
MODBUS_TYPE_RTU_OVER_TCP = "rtuovertcp"
MODBUS_TYPE_SERIAL = "serial"
DEFAULT_MODBUS_TYPE = MODBUS_TYPE_TCP

MODBUS_TYPES = [
    {"value": MODBUS_TYPE_TCP, "label": "TCP"},
    {"value": MODBUS_TYPE_UDP, "label": "UDP"},
    {"value": MODBUS_TYPE_RTU_OVER_TCP, "label": "RTU over TCP"},
    {"value": MODBUS_TYPE_SERIAL, "label": "Serial"}
]

# Baud rate choices
DEFAULT_SERIAL_BAUDRATE = 19200
SERIAL_BAUDRATES = [
    {"value": "300", "label": "300 bps"},
    {"value": "600", "label": "600 bps"},
    {"value": "1200", "label": "1 200 bps"},
    {"value": "2400", "label": "2 400 bps"},
    {"value": "4800", "label": "4 800 bps"},
    {"value": "9600", "label": "9 600 bps"},
    {"value": "14400", "label": "14 400 bps"},
    {"value": "19200", "label": "19 200 bps"},
    {"value": "28800", "label": "28 800 bps"},
    {"value": "38400", "label": "38 400 bps"},
    {"value": "57600", "label": "57 600 bps"},
    {"value": "115200", "label": "115 200 bps"},
    {"value": "230400", "label": "230 400 bps"},
    {"value": "460800", "label": "460 800 bps"},
    {"value": "921600", "label": "921 600 bps"}
]

# Byte size (data bits) choices
DEFAULT_SERIAL_BYTESIZE = 8
SERIAL_BYTESIZES = [
    {"value": "8", "label": "8 bits"},
    {"value": "7", "label": "7 bits"},
    {"value": "6", "label": "6 bits"},
    {"value": "5", "label": "5 bits"}
]

# Parity choices
DEFAULT_PARITY = "N"
SERIAL_PARITIES = [
    {"value": "N", "label": "None"},
    {"value": "E", "label": "Even"},
    {"value": "O", "label": "Odd"}
]

# Stop bits
DEFAULT_STOPBITS = 1
SERIAL_STOPBITS = [
    {"value": "1", "label": "1 bit"},
    {"value": "2", "label": "2 bits"}
]

# Modbus Queue wait timeout (seconds)
QUEUE_TIMEOUT = 1.0
