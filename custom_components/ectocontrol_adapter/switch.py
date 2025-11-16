import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .mixins import ModbusUniqIdMixin
from .registers import SWITCH_INPUT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up switch entities  """
    data = hass.data[DOMAIN][config_entry.entry_id]
    master_coordinator = data["master_coordinator"]
    write_registers = data["write_registers"]

    entities = []

    for register, config in write_registers.items():
        if config.get("input_type") == SWITCH_INPUT:
            entities.append(ModbusSwitch(hass, master_coordinator, register, config))

    async_add_entities(entities)


class ModbusSwitch(ModbusUniqIdMixin, SwitchEntity, RestoreEntity):
    """ Modbus Switch entity """

    def __init__(self, hass, master_coordinator, register_addr, register_config):
        self.hass = hass
        self.coordinator = master_coordinator
        self.register_addr = register_addr
        self.register_config = register_config

        self._attr_has_entity_name = True
        self._attr_translation_key = self.register_config.get("name")
        self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{register_addr:#06x}"
        self._attr_is_on = None  # Initial state is unknown
        self._attr_device_class = register_config.get("device_class")
        self._attr_entity_category = register_config.get("category")

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        if last_state is not None:
            if last_state.state == "on":
                self._attr_is_on = True
            elif last_state.state == "off":
                self._attr_is_on = False
            else:
                self._attr_is_on = None

    async def async_turn_on(self, **kwargs):
        wrval = self.register_config["on_value"]
        success = await self.coordinator.write_registers(
            address=self.register_addr, values=[wrval])

        if success:
            self._attr_is_on = True
            self.async_write_ha_state()
            _LOGGER.info(f"Successfully set '{self._attr_translation_key}' to '{wrval}'")
        else:
            raise Exception(f"Failed to write value '{wrval}' to register={self.register_addr:#06x}")

    async def async_turn_off(self, **kwargs):
        wrval = self.register_config["off_value"]
        success = await self.coordinator.write_registers(
            address=self.register_addr, values=[wrval])

        if success:
            self._attr_is_on = False
            self.async_write_ha_state()
            _LOGGER.info(f"Successfully set '{self._attr_translation_key}' to '{wrval}'")
        else:
            raise Exception(f"Failed to write value '{wrval}' to register={self.register_addr:#06x}")

    @property
    def assumed_state(self) -> bool:
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self):
        return self.register_config.get("icon")
