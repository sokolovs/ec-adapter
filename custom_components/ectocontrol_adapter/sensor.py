import logging
import struct

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers import BM_BINARY, BM_VALUE, BYTE_TYPES, REGISTERS, REG_TYPE_MAPPING

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
                    if mask_config["type"] == BM_BINARY:
                        sensor = ModbusBinarySensor(coordinator, register_addr, register_config, mask)
                        sensors.append(sensor)
                    elif mask_config["type"] == BM_VALUE:
                        sensor = ModbusSensor(coordinator, register_addr, register_config, mask)
                        sensors.append(sensor)

    async_add_entities(sensors, True)


class ModbusSensorMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_raw_value(self, raw_data):
        """Convert raw register data to sensor value."""
        try:
            data_type = self.register_config.get("data_type")
            scale = self.register_config.get("scale", 1.0)
            count = self.register_config.get("count", 1)

            if not data_type:
                return raw_data[0] if raw_data else None

            # Convert registers to bytes
            byte_data = b''
            for register in raw_data:
                byte_data += register.to_bytes(2, byteorder='big')

            # Check config count for one byte values
            if data_type in BYTE_TYPES and count > 1:
                _LOGGER.error(
                    "Invalid configuration for register %s: "
                    "8-bit data types require count=1, got count=%d",
                    self.register_addr, count
                )
                return None

            struct_data_type = REG_TYPE_MAPPING[data_type]
            if data_type in BYTE_TYPES:  # for one byte values
                value = struct.unpack(f'>{struct_data_type}', bytes([byte_data[1]]))[0]
            else:
                value = struct.unpack(f'>{struct_data_type}', byte_data)[0]

            # Apply scaling if needed
            if scale != 1.0:
                value *= scale

            return value

        except Exception as e:
            _LOGGER.error("Error converting register %s data: %s", self.register_addr, e)
            return None


class ModbusSensor(ModbusSensorMixin, CoordinatorEntity, SensorEntity):
    """ Modbus Sensor. """

    def __init__(self, coordinator, register_addr, register_config, bitmask=None):
        """ Initialize the sensor. """
        super().__init__(coordinator)
        self.register_addr = register_addr
        self.register_config = register_config

        self.bitmask = None
        self.bitmask_config = {}
        if isinstance(bitmask, int):
            self.bitmask = bitmask
            self.bitmask_config = register_config["bitmasks"][bitmask]

        # Display values
        self.choices = self.bitmask_config.get('choices') or self.register_config.get('choices')

        # Entity attributes
        self._attr_has_entity_name = True
        if self.bitmask is not None:
            self._attr_translation_key = self.bitmask_config.get("name")
            if self._attr_translation_key is None:
                self._attr_name = f"Register {register_addr:#06x} bitmask {bitmask}"
            self._attr_unique_id = f"{DOMAIN}_{register_addr:#06x}_bitmask{bitmask}"
            self._attr_device_class = self.bitmask_config.get("device_class")
            self._attr_native_unit_of_measurement = self.bitmask_config.get("unit_of_measurement")
        else:
            self._attr_translation_key = register_config.get("name")
            if self._attr_translation_key is None:
                self._attr_name = f"Register {register_addr:#06x}"
            self._attr_unique_id = f"{DOMAIN}_{register_addr:#06x}"
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
        if raw_value is not None and self.bitmask is not None:
            raw_value &= self.bitmask
            if "rshift" in self.bitmask_config:
                raw_value >>= self.bitmask_config["rshift"]

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
        if self._attr_translation_key is None:
            self._attr_name = f"Register {register_addr:#06x} bitmask {bitmask}"
        self._attr_unique_id = f"{DOMAIN}_{register_addr:#06x}_bitmask{bitmask}"
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
