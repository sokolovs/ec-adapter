import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .mixins import ModbusSensorMixin
from .registers import BM_BINARY, REGISTERS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up sensors. """
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinators = data["coordinators"]
    register_groups = data["register_groups"]

    sensors = []

    # Create sensors for each coordinator
    for scan_interval, coordinator in coordinators.items():
        registers = register_groups[scan_interval]

        for register_addr in registers:
            register_config = REGISTERS[register_addr]
            if "bitmasks" in register_config:
                for mask, mask_config in register_config["bitmasks"].items():
                    if mask_config["type"] == BM_BINARY:
                        sensor = ModbusBinarySensor(coordinator, register_addr, register_config, mask)
                        sensors.append(sensor)

    async_add_entities(sensors, True)


class ModbusBinarySensor(ModbusSensorMixin, CoordinatorEntity, BinarySensorEntity):
    """ Binary sensor for bitmasks values. """

    def __init__(self, coordinator, register_addr, register_config, bitmask):
        super().__init__(coordinator)
        self.register_addr = register_addr
        self.register_config = register_config
        self.bitmask = bitmask
        self.bitmask_config = register_config["bitmasks"][bitmask]

        # Entity attributes
        self._attr_has_entity_name = True
        self._attr_translation_key = self.bitmask_config.get("name")
        self._attr_unique_id = (
            f"{self._unique_id_prefix}_{self._attr_translation_key}_"
            f"{register_addr:#06x}_mask_{bitmask:#08x}"
        )
        self._attr_device_class = self.bitmask_config.get("device_class")

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    @property
    def is_on(self):
        """ Return True if the bits is set. """
        if self.coordinator.data is None:
            return None

        raw_data = self.coordinator.data.get(self.register_addr)
        if raw_data is None:
            return None

        raw_value = self._get_raw_value(raw_data)
        if raw_value is None:
            return None

        return bool(raw_value & self.bitmask)
