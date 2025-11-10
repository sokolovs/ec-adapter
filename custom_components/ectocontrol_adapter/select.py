import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .mixins import ModbusUniqIdMixin
from .registers import SELECT_INPUT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up select entities  """
    data = hass.data[DOMAIN][config_entry.entry_id]
    master_coordinator = data["master_coordinator"]
    write_registers = data["write_registers"]

    entities = []

    for register, config in write_registers.items():
        if config.get("input_type") == SELECT_INPUT:
            entities.append(ModbusSelect(hass, master_coordinator, register, config))

    async_add_entities(entities)


class ModbusSelect(ModbusUniqIdMixin, SelectEntity, RestoreEntity):
    """ Modbus Select entity """

    def __init__(self, hass, master_coordinator, register_addr, register_config):
        self.hass = hass
        self.coordinator = master_coordinator
        self.register_addr = register_addr
        self.register_config = register_config
        self.choices = register_config.get("choices")

        self._attr_has_entity_name = True
        self._attr_translation_key = self.register_config.get("name")
        self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{register_addr:#06x}"
        self._attr_options = list(self.choices.keys())
        self._attr_current_option = register_config.get("initial_value")
        self._attr_entity_category = register_config.get("category")

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state in self._attr_options:
            self._attr_current_option = last_state.state

    async def async_select_option(self, option: str) -> None:
        """ Change the selected option """
        if option not in self.choices:
            raise Exception(f"Unknown option '{option}' for register={self.register_addr:#06x}")

        wrval = self.choices[option]
        success = await self.coordinator.write_registers(
            address=self.register_addr, values=[wrval])

        if success:
            self._attr_current_option = option
            self.async_write_ha_state()
            _LOGGER.info(f"Successfully set '{self._attr_translation_key}' to '{option}'")
        else:
            raise Exception(f"Failed to write value {wrval} to register={self.register_addr:#06x}")

    @property
    def assumed_state(self) -> bool:
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self):
        return self.register_config.get("icon")
