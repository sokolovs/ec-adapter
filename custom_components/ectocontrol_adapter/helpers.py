from pymodbus import FramerType
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient
)

from .const import *  # noqa F403


def create_modbus_client(config_data):
    """ Returns a Modbus client instance based on the `config_data` """
    if config_data[OPT_MODBUS_TYPE] == MODBUS_TYPE_TCP:
        return AsyncModbusTcpClient(
            host=config_data[OPT_HOST],
            port=int(config_data[OPT_PORT]),
            timeout=int(config_data[OPT_RESPONSE_TIMEOUT])
        )
    elif config_data[OPT_MODBUS_TYPE] == MODBUS_TYPE_UDP:
        return AsyncModbusUdpClient(
            host=config_data[OPT_HOST],
            port=int(config_data[OPT_PORT]),
            timeout=int(config_data[OPT_RESPONSE_TIMEOUT])
        )
    elif config_data[OPT_MODBUS_TYPE] == MODBUS_TYPE_RTU_OVER_TCP:
        return AsyncModbusTcpClient(
            host=config_data[OPT_HOST],
            port=int(config_data[OPT_PORT]),
            timeout=int(config_data[OPT_RESPONSE_TIMEOUT]),
            framer=FramerType.RTU
        )
    elif config_data[OPT_MODBUS_TYPE] == MODBUS_TYPE_SERIAL:
        return AsyncModbusSerialClient(
            port=config_data[OPT_DEVICE],
            baudrate=int(config_data[OPT_BAUDRATE]),
            bytesize=int(config_data[OPT_BYTESIZE]),
            parity=config_data[OPT_PARITY],
            stopbits=int(config_data[OPT_STOPBITS]),
            timeout=int(config_data[OPT_RESPONSE_TIMEOUT])
        )
