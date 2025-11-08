""" ectoControl Adapter """
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import ModbusReadCoordinator, ModbusWriteCoordinator
from .registers import REGISTERS_R, REGISTERS_W, REG_DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Set up sensors from a config entry. """
    hass.data.setdefault(DOMAIN, {})

    # Create device
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name=config_entry.options.get("name") or config_entry.data.get("name"),
        manufacturer="ectoControl"
    )

    # Create and start write coordinator
    write_coordinator = ModbusWriteCoordinator(
        hass=hass,
        config_entry=config_entry
    )
    await write_coordinator.async_start()

    # Group registers by scan interval
    read_register_groups = {}
    for register_addr, config in REGISTERS_R.items():
        scan_interval = config.get("scan_interval", REG_DEFAULT_SCAN_INTERVAL)
        if scan_interval not in read_register_groups:
            read_register_groups[scan_interval] = []
        read_register_groups[scan_interval].append((register_addr, config))

    # Create coordinators for each scan interval group
    read_coordinators = {}
    for scan_interval, registers in read_register_groups.items():
        read_coordinator = ModbusReadCoordinator(
            hass=hass,
            config_entry=config_entry,
            registers=registers,
            scan_interval=scan_interval
        )

        # Fetch initial data
        await read_coordinator.async_config_entry_first_refresh()
        read_coordinators[scan_interval] = read_coordinator

    hass.data[DOMAIN][config_entry.entry_id] = {
        "device_id": device.id,
        "read_coordinators": read_coordinators,
        "read_register_groups": read_register_groups,
        "write_coordinator": write_coordinator,
        "write_registers": REGISTERS_W
    }

    # Set up sensors
    await hass.config_entries.async_forward_entry_setups(
        config_entry, [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER])

    return True


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Update options for entry that was configured via user interface. """
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Unload a config entry. """
    await hass.config_entries.async_forward_entry_unload(
        config_entry, [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER])
    write_coordinator = hass.data[DOMAIN][config_entry.entry_id]["write_coordinator"]
    await write_coordinator.async_stop()
    return True
