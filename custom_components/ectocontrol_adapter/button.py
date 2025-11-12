import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .mixins import ModbusUniqIdMixin
from .registers import BUTTON_INPUT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up select entities  """
    data = hass.data[DOMAIN][config_entry.entry_id]
    master_coordinator = data["master_coordinator"]
    write_registers = data["write_registers"]

    entities = []

    for register_addr, register_config in write_registers.items():
        if register_config.get("input_type") == BUTTON_INPUT:
            if not ("buttons" in register_config and len(register_config["buttons"])):
                continue

            for button_config in register_config["buttons"]:
                entities.append(ModbusButton(
                    hass,
                    master_coordinator,
                    register_addr,
                    register_config,
                    button_config
                ))

    async_add_entities(entities)


class ModbusButton(ModbusUniqIdMixin, ButtonEntity):
    """ Modbus Button entity """

    def __init__(self, hass, master_coordinator, register_addr, register_config, button_config):
        self.hass = hass
        self.coordinator = master_coordinator
        self.register_addr = register_addr
        self.register_config = register_config
        self.button_config = button_config

        self._attr_has_entity_name = True
        self._attr_translation_key = f"{register_config.get('name')}_{button_config.get('name')}"
        self._attr_unique_id = f"{self._unique_id_prefix}_{self._attr_translation_key}_{register_addr:#06x}"
        self._attr_device_class = button_config.get("device_class") or register_config.get("device_class")
        self._attr_entity_category = button_config.get("category") or register_config.get("category")

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    async def async_press(self) -> None:
        """ Press button """
        wrval = self.button_config.get("value")
        if not isinstance(wrval, int):
            raise Exception(f"Can not write value '{wrval}' to register={self.register_addr:#06x}")

        success = await self.coordinator.write_registers(
            address=self.register_addr,
            values=[wrval],
            status_register=self.register_config.get("status_register"))

        if success:
            _LOGGER.info(f"Successfully set '{self._attr_translation_key}' to '{wrval}'")
        else:
            raise Exception(f"Failed to write value '{wrval}' to register={self.register_addr:#06x}")

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self):
        return self.button_config.get("icon") or self.register_config.get("icon")
