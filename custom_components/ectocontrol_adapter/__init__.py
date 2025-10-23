""" ectoControl Adapter Integration. """
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from pymodbus import FramerType
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient
)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Set up sensor from a config entry. """
    await hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SENSOR])
    return True


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Update options for entry that was configured via user interface. """
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Unload a config entry. """
    await hass.config_entries.async_forward_entry_unload(config_entry, Platform.SENSOR)
    return True


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
