import logging
import struct

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .registers import BYTE_TYPES, REGISTERS

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

    async_add_entities(sensors, True)


class ModbusSensor(CoordinatorEntity, SensorEntity):
    """ Modbus Sensor. """

    def __init__(self, coordinator, register_addr, register_config):
        """ Initialize the sensor. """
        super().__init__(coordinator)
        self.register_addr = register_addr
        self.register_config = register_config

        # Entity attributes
        self._attr_name = register_config.get("name", f"Register {register_addr:#06x}")
        self._attr_unique_id = f"{DOMAIN}_{register_addr:#06x}"
        self._attr_device_class = register_config.get("device_class")
        self._attr_native_unit_of_measurement = register_config.get("unit_of_measurement")

        # Initial state
        self._attr_native_value = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        raw_data = self.coordinator.data.get(self.register_addr)
        if raw_data is None:
            return None

        return self._convert_raw_value(raw_data)

    def _convert_raw_value(self, raw_data):
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

            if data_type in BYTE_TYPES:  # for one byte values
                if len(byte_data) >= 1:
                    value = byte_data[1]
                    if data_type == 'b':
                        value = struct.unpack('b', bytes([value]))[0]
            else:
                value = struct.unpack(f'>{data_type}', byte_data)[0]

            # Apply scaling if needed
            if scale != 1.0:
                value *= scale

            return value

        except Exception as e:
            _LOGGER.error("Error converting register %s data: %s", self.register_addr, e)
            return None

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {
            "register_address": self.register_addr,
            "data_type": self.register_config.get("data_type"),
            "register_count": self.register_config.get("count", 1)
        }
