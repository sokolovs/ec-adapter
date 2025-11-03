import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .mixins import ModbusSensorMixin
from .registers import BM_VALUE, REGISTERS

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
            sensor = ModbusSensor(coordinator, register_addr, register_config)
            sensors.append(sensor)

            if "bitmasks" in register_config:
                for mask, mask_config in register_config["bitmasks"].items():
                    if mask_config["type"] == BM_VALUE:
                        sensor = ModbusSensor(coordinator, register_addr, register_config, mask)
                        sensors.append(sensor)

            if "converters" in register_config:
                for conv_name in register_config["converters"].keys():
                    sensor = ModbusSensor(
                        coordinator, register_addr, register_config,
                        bitmask=None, conv_name=conv_name)
                    sensors.append(sensor)

    async_add_entities(sensors, True)


class ModbusSensor(ModbusSensorMixin, CoordinatorEntity, SensorEntity):
    """ Modbus Sensor. """

    def __init__(self, coordinator, register_addr, register_config, bitmask=None, conv_name=None):
        """ Initialize the sensor. """
        super().__init__(coordinator)
        self.register_addr = register_addr
        self.register_config = register_config

        self.bitmask = None
        self.bitmask_config = {}
        if isinstance(bitmask, int):
            self.bitmask = bitmask
            self.bitmask_config = register_config["bitmasks"][bitmask]

        self.conv_name = conv_name
        self.conv = None
        self.conv_config = {}
        if isinstance(conv_name, str):
            self.conv_config = register_config["converters"][conv_name]
            self.conv = self.conv_config["converter"]

        # Display values
        self.choices = self.bitmask_config.get('choices') or self.register_config.get('choices')

        # Entity attributes
        self._attr_has_entity_name = True
        if self.bitmask is not None:
            self._attr_translation_key = self.bitmask_config.get("name")
            self._attr_unique_id = (
                f"{self._unique_id_prefix}_{self._attr_translation_key}_"
                f"{register_addr:#06x}_mask_{bitmask:#08x}"
            )
            self._attr_device_class = self.bitmask_config.get("device_class")
            self._attr_native_unit_of_measurement = self.bitmask_config.get("unit_of_measurement")
        elif self.conv is not None:
            self._attr_translation_key = self.conv_config.get("name")
            self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{conv_name}"
            self._attr_device_class = self.conv_config.get("device_class")
            self._attr_native_unit_of_measurement = self.conv_config.get("unit_of_measurement")
        else:
            self._attr_translation_key = register_config.get("name")
            self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{register_addr:#06x}"
            self._attr_device_class = register_config.get("device_class")
            self._attr_native_unit_of_measurement = register_config.get("unit_of_measurement")

        # Initial state
        self._attr_native_value = None

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        raw_data = self.coordinator.data.get(self.register_addr)
        if raw_data is None:
            return None

        raw_value = self._get_raw_value(raw_data)
        if raw_value is None:
            return

        if self.bitmask is not None:
            raw_value &= self.bitmask
            if "rshift" in self.bitmask_config:
                raw_value >>= self.bitmask_config["rshift"]
        elif self.conv is not None:
            raw_value = self.conv(raw_value)

        if self.choices and raw_value in self.choices:
            return self.choices[raw_value]

        return raw_value

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {
            "register_address": hex(self.register_addr),
            "data_type": self.register_config.get("data_type"),
            "register_count": self.register_config.get("count", 1)
        }
