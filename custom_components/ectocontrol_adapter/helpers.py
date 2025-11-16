from pymodbus import FramerType
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient
)


def get_config_value(config_entry, key, default=None):
    """
    Returns an option from the configuration according to the search priority:
        options > data > default
    """
    if config_entry:
        if key in config_entry.options:
            return config_entry.options.get(key)
        if key in config_entry.data:
            return config_entry.data.get(key)
    return default


def create_modbus_client(config_data):
    """ Returns a Modbus client instance based on the `config_data` """
    if config_data["modbus_type"] == "tcp":
        return AsyncModbusTcpClient(
            host=config_data["host"],
            port=config_data["port"],
            timeout=config_data["response_timeout"]
        )
    elif config_data["modbus_type"] == "udp":
        return AsyncModbusUdpClient(
            host=config_data["host"],
            port=config_data["port"],
            timeout=config_data["response_timeout"]
        )
    elif config_data["modbus_type"] == "rtuovertcp":
        return AsyncModbusTcpClient(
            host=config_data["host"],
            port=config_data["port"],
            timeout=config_data["response_timeout"],
            framer=FramerType.RTU
        )
    elif config_data["modbus_type"] == "serial":
        return AsyncModbusSerialClient(
            port=config_data["device"],
            baudrate=config_data["baudrate"],
            bytesize=config_data["bytesize"],
            parity=config_data["parity"],
            stopbits=config_data["stopbits"],
            timeout=config_data["response_timeout"]
        )
