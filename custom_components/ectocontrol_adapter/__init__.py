""" ectoControl Adapter Integration. """
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import ModbusCoordinator
from .registers import REGISTERS, REG_DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Set up sensors from a config entry. """
    hass.data.setdefault(DOMAIN, {})

    # Group registers by scan interval
    register_groups = {}
    for register_addr, config in REGISTERS.items():
        scan_interval = config.get("scan_interval", REG_DEFAULT_SCAN_INTERVAL)
        if scan_interval not in register_groups:
            register_groups[scan_interval] = []
        register_groups[scan_interval].append(register_addr)

    # Create coordinators for each scan interval group
    coordinators = {}
    for scan_interval, registers in register_groups.items():
        coordinator = ModbusCoordinator(
            hass=hass,
            config_entry=config_entry,
            registers=registers,
            scan_interval=scan_interval
        )

        # Fetch initial data
        await coordinator.async_config_entry_first_refresh()
        coordinators[scan_interval] = coordinator

    hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinators": coordinators,
        "register_groups": register_groups
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name="ectoControl Adapter",
        manufacturer="ectoControl"
    )

    # Set up sensors
    await hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SENSOR])

    return True


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Update options for entry that was configured via user interface. """
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Unload a config entry. """
    await hass.config_entries.async_forward_entry_unload(config_entry, Platform.SENSOR)
    return True
