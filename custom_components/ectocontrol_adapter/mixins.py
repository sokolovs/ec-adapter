import logging
import struct

from .const import DOMAIN
from .helpers import get_config_value
from .registers import BYTE_TYPES, REG_TYPE_MAPPING

_LOGGER = logging.getLogger(__name__)


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

    @property
    def _unique_id_prefix(self):
        mb_type = get_config_value(self.coordinator.config_entry, "modbus_type")
        if mb_type == "serial":
            device = get_config_value(self.coordinator.config_entry, "device")
            return f"{DOMAIN}_{mb_type}_{device}"
        else:
            host = get_config_value(self.coordinator.config_entry, "host")
            port = get_config_value(self.coordinator.config_entry, "port")
            return f"{DOMAIN}_{mb_type}_{host}_{port}"
