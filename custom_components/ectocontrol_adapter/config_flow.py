import logging

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType
)

import voluptuous as vol

from .const import *  # noqa F403
from .helpers import create_modbus_client
from .registers import REGISTERS_R, REG_R_ADAPTER_UPTIME

_LOGGER = logging.getLogger(__name__)


async def create_schema(hass, config_entry=None, user_input=None, type="init"):
    """ Common schema for ConfigFlow and OptionsFlow."""

    if type == "serial":
        return vol.Schema({
            # Serial settings
            vol.Required(OPT_DEVICE, default=DEFAULT_DEVICE):
                TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),

            vol.Required(OPT_BAUDRATE, default=str(DEFAULT_SERIAL_BAUDRATE)):
                SelectSelector(SelectSelectorConfig(
                    options=SERIAL_BAUDRATES, mode=SelectSelectorMode.DROPDOWN)),

            vol.Required(OPT_BYTESIZE, default=str(DEFAULT_SERIAL_BYTESIZE)):
                SelectSelector(SelectSelectorConfig(
                    options=SERIAL_BYTESIZES, mode=SelectSelectorMode.DROPDOWN)),

            vol.Required(OPT_PARITY, default=DEFAULT_PARITY):
                SelectSelector(SelectSelectorConfig(
                    options=SERIAL_PARITIES, mode=SelectSelectorMode.DROPDOWN)),

            vol.Required(OPT_STOPBITS, default=str(DEFAULT_STOPBITS)):
                SelectSelector(SelectSelectorConfig(
                    options=SERIAL_STOPBITS, mode=SelectSelectorMode.DROPDOWN)),
        })
    elif type in ("tcp", "udp", "rtuovertcp"):
        return vol.Schema({
            # Host + Port settings
            vol.Required(OPT_HOST): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),

            vol.Required(OPT_PORT, default=DEFAULT_PORT):
                NumberSelector(NumberSelectorConfig(min=1, max=65535, mode=NumberSelectorMode.BOX)),

        })
    else:
        return vol.Schema({
            vol.Required(OPT_NAME): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),

            # Settings
            vol.Required(OPT_RESPONSE_TIMEOUT, default=DEFAULT_RESPONSE_TIMEOUT):
                NumberSelector(NumberSelectorConfig(min=1, max=10, mode=NumberSelectorMode.BOX)),

            vol.Required(OPT_MODBUS_TYPE, default=DEFAULT_MODBUS_TYPE):
                SelectSelector(SelectSelectorConfig(
                    options=MODBUS_TYPES, mode=SelectSelectorMode.DROPDOWN)),

            vol.Required(OPT_SLAVE, default=DEFAULT_SLAVE_ID):
                NumberSelector(NumberSelectorConfig(min=0, max=248, mode=NumberSelectorMode.BOX)),
        })


async def check_user_input(user_input):
    errors = {}
    client = create_modbus_client(user_input)
    try:
        result = await client.connect()
        if not result:
            errors["base"] = "ec_modbus_connect_error"
            _LOGGER.error("Failed to connect to Modbus device")
        else:
            _LOGGER.info("Successfully connected to Modbus device")

            adapter_uptime = await client.read_holding_registers(
                address=REG_R_ADAPTER_UPTIME,
                count=REGISTERS_R[REG_R_ADAPTER_UPTIME]["count"],
                device_id=int(user_input[OPT_SLAVE])
            )

            if adapter_uptime is None or adapter_uptime.isError():
                errors["base"] = "ec_uptime_reading_error"
                _LOGGER.error(
                    "Modbus error reading uptime from adapter: %s", adapter_uptime)
            else:
                _LOGGER.info("Modbus reading uptime value: %s" % adapter_uptime.registers)

    except Exception as e:
        errors["base"] = "ec_modbus_connect_error"
        _LOGGER.error("Failed to connect to Modbus device: %s" % e)
    return errors


class ECAdapterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ Handle a config flow for ectoControl Adapter. """

    VERSION = 1

    def __init__(self):
        self.config_data = {}
        self.next_step = None

    async def async_step_user(self, user_input=None):
        """ Handle the initial step. """
        if self.next_step:
            return await self.next_step(user_input)

        _LOGGER.debug("Request to create config (init step): %s", user_input)

        if user_input is not None:
            self.config_data.update(user_input)
            self.next_step = self.async_step_connection
            return await self.async_step_connection()

        schema = await create_schema(
            hass=self.hass,
            user_input=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )

    async def async_step_connection(self, user_input=None):
        """ Handle the connection step. """
        _LOGGER.debug("Request to create config (connection step): %s", user_input)

        errors = {}
        if user_input is not None:
            self.config_data.update(user_input)
            errors = await check_user_input(self.config_data)
            if not errors:
                return self.async_create_entry(
                    title=self.config_data[OPT_NAME],
                    data=self.config_data)

        schema = await create_schema(
            hass=self.hass,
            user_input=user_input,
            type=self.config_data[OPT_MODBUS_TYPE])
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(schema, user_input or {}),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ECAdapterOptionsFlow(config_entry)


class ECAdapterOptionsFlow(config_entries.OptionsFlow):
    """ Handle options flow for ectoControl Adapter. """

    def __init__(self, config_entry):
        if HA_VERSION < '2024.12':
            self.config_entry = config_entry
        self.config_data = {}
        self.next_step = None

    async def async_step_init(self, user_input=None):
        """ Manage the options. """
        if self.next_step:
            return await self.next_step(user_input)

        _LOGGER.debug("Request to update options (init step): %s", user_input)

        errors = {}
        if user_input is not None:
            self.config_data.update(user_input)
            self.next_step = self.async_step_connection
            return await self.async_step_connection()

        schema = await create_schema(
            hass=self.hass,
            config_entry=self.config_entry,
            user_input=user_input
        )

        options = self.config_entry.options or self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, options),
            errors=errors
        )

    async def async_step_connection(self, user_input=None):
        """ Handle the connection step. """
        _LOGGER.debug("Request to update options (connection step): %s", user_input)

        errors = {}
        if user_input is not None:
            self.config_data.update(user_input)
            errors = await check_user_input(self.config_data)
            if not errors:
                # Update configuration
                self.hass.config_entries.async_update_entry(
                    self.config_entry, options=self.config_data)

                # Send signal to subscribers
                async_dispatcher_send(self.hass, SENSOR_UPDATE_SIGNAL)

                return self.async_create_entry(title="", data=self.config_data)

        schema = await create_schema(
            hass=self.hass,
            config_entry=self.config_entry,
            user_input=user_input,
            type=self.config_data[OPT_MODBUS_TYPE])

        options = user_input or self.config_entry.options or self.config_entry.data or {}
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, options),
            errors=errors
        )
