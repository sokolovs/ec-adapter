import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .mixins import ModbusUniqIdMixin
from .registers import NUMBER_INPUT, REG_DEFAULT_NUMBER_STEP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up number entities  """
    data = hass.data[DOMAIN][config_entry.entry_id]
    write_coordinator = data["write_coordinator"]
    write_registers = data["write_registers"]

    entities = []

    for register, config in write_registers.items():
        if config.get("input_type") == NUMBER_INPUT:
            entities.append(ModbusNumber(hass, write_coordinator, register, config))

    async_add_entities(entities)


class ModbusNumber(ModbusUniqIdMixin, NumberEntity):
    """ Modbus Number entity """

    def __init__(self, hass, write_coordinator, register_addr, register_config):
        self._hass = hass
        self.coordinator = write_coordinator
        self.register_addr = register_addr
        self.register_config = register_config

        self._attr_mode = NumberMode.BOX
        self._attr_has_entity_name = True
        self._attr_translation_key = self.register_config.get("name")
        self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{register_addr:#06x}"

        self._attr_native_min_value = register_config["min_value"]
        self._attr_native_max_value = register_config["max_value"]
        self._attr_native_value = register_config.get("initial_value")
        self._attr_native_step = register_config.get("step", REG_DEFAULT_NUMBER_STEP)
        self._attr_native_unit_of_measurement = register_config.get("unit_of_measurement")

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    async def async_set_native_value(self, value: float) -> None:
        """ Set value via write coordinator """
        intval = int(value)
        success = await self.coordinator.submit_write_operation(
            register=self.register_addr, value=[intval])

        if success:
            self._attr_native_value = value
            self.async_write_ha_state()
            _LOGGER.info("Successfully set %s to %s", self._attr_translation_key, intval)
        else:
            raise Exception(f"Failed to write value {intval} to register={self.register_addr:#06x}")

    @property
    def should_poll(self) -> bool:
        return False
