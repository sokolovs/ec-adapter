import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .mixins import ModbusUniqIdMixin
from .registers import NUMBER_INPUT, REG_DEFAULT_NUMBER_STEP

_LOGGER = logging.getLogger(__name__)
_SUBSCRIBE_ATTEMPTS_DELAY = 5


async def async_setup_entry(hass, config_entry, async_add_entities):
    """ Set up number entities  """
    data = hass.data[DOMAIN][config_entry.entry_id]
    master_coordinator = data["master_coordinator"]
    write_registers = data["write_registers"]

    entities = []

    for register, config in write_registers.items():
        if config.get("input_type") == NUMBER_INPUT:
            entities.append(ModbusNumber(hass, master_coordinator, register, config))

    async_add_entities(entities)


class ModbusNumber(ModbusUniqIdMixin, NumberEntity, RestoreEntity):
    """ Modbus Number entity """

    def __init__(self, hass, master_coordinator, register_addr, register_config):
        self.hass = hass
        self.coordinator = master_coordinator
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
        self._attr_device_class = register_config.get("device_class")
        self._attr_entity_category = register_config.get("category")

        # Write after turn on
        self.write_after_connected = None
        if (
                "write_after_connected" in register_config and
                isinstance(register_config["write_after_connected"], tuple) and
                len(register_config["write_after_connected"]) == 2):
            self.write_after_connected = self.register_config["write_after_connected"]

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)}
        )

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()

        # Restore last state and write to register (optional)
        if last_state is not None:
            self._attr_native_value = int(last_state.state)

            # Subscribe to binary sensor updates and component loaded event
            if self.write_after_connected is not None:
                # Write register immediatly
                _LOGGER.debug(
                    f"'{self._attr_translation_key}' added to HA. "
                    f"Write last state to register={self.register_addr:#06x}")
                await self.async_set_native_value(value=float(last_state.state))

        # Subscribe to adapter connected event
        if self.write_after_connected is not None:
            async_call_later(
                hass=self.hass,
                delay=_SUBSCRIBE_ATTEMPTS_DELAY,
                action=lambda _: self._subscribe_with_retry()
            )

    async def async_set_native_value(self, value: float) -> None:
        """ Set value via write coordinator """
        intval = wrval = int(value)
        scale = self.register_config.get("scale")
        if scale is not None and scale > 0:
            wrval *= scale  # real write value

        success = await self.coordinator.write_registers(
            address=self.register_addr, values=[wrval])

        if success:
            self._attr_native_value = intval
            self.async_write_ha_state()
            _LOGGER.info(f"Successfully set '{self._attr_translation_key}' to '{intval}'")
        else:
            raise Exception(f"Failed to write value '{intval}' to register={self.register_addr:#06x}")

    def _subscribe_with_retry(self, attempt=1, max_attempts=10):
        """ Subscribe to binary sensor updates (i.e. connectivity) """
        sensor_addr, sensor_name = self.write_after_connected
        reg = entity_registry.async_get(self.hass)

        sensor_unique_id = f"{self._unique_id_prefix}_{sensor_name}_{sensor_addr:#06x}"
        entity_id = reg.async_get_entity_id(Platform.BINARY_SENSOR, DOMAIN, sensor_unique_id)
        if entity_id:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, entity_id, self._handle_write_after_connected))
            _LOGGER.debug(f"Subscribe to '{entity_id}' for '{self._attr_translation_key}': SUCCESS")
        else:
            if attempt < max_attempts:
                _LOGGER.debug(
                    f"Subscription attempt '{attempt}' to '{sensor_unique_id}' "
                    f"failed, try again in 5 seconds...")
                async_call_later(
                    hass=self.hass,
                    delay=_SUBSCRIBE_ATTEMPTS_DELAY,
                    action=lambda _: self._subscribe_with_retry(attempt + 1, max_attempts)
                )
            else:
                _LOGGER.error(
                    f"Unable to find entity '{sensor_unique_id}' "
                    f"to subscribe to after '{max_attempts}' attempts")

    async def _handle_write_after_connected(self, event):
        """ Processing updates to monitored binary sensor """
        _LOGGER.debug(
            f"Sensor state change detected: '{event.data.get('entity_id')}', "
            f"subscriber is: '{self._attr_translation_key}'")

        new_state = event.data.get('new_state')
        if new_state.state == "off":
            return

        # Write current value or last state
        write_value = self._attr_native_value
        if write_value is None and (last_state := await self.async_get_last_state()):
            write_value = float(last_state.state)

        if write_value is not None:
            await self.async_set_native_value(value=write_value)

    @property
    def assumed_state(self) -> bool:
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self):
        return self.register_config.get("icon")
