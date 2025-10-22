import logging

from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.translation import async_get_translations

import voluptuous as vol

from . import get_config_value
from .const import *

_LOGGER = logging.getLogger(__name__)


async def get_user_language(hass):
    user_language = hass.data.get("language")
    return user_language if user_language else hass.config.language


async def get_translation(hass, key, default="Not found..."):
    language = await get_user_language(hass)
    translations = await async_get_translations(hass, language, "common", [])
    return translations.get(key, default)


async def create_schema(hass, config_entry=None, user_input=None, type="init"):
    """ Common schema for ConfigFlow and OptionsFlow."""

    def get_config(key, default=None):
        if user_input is not None:
            return user_input.get(key, default)
        return get_config_value(config_entry, key, default)

    if type == "serial":
        return vol.Schema({
            # Serial settings
            vol.Required(
                "device",
                default=get_config("port", "/dev/ttyUSB0")): str,

            vol.Required(
                "baudrate",
                default=get_config("baudrate", DEFAULT_SERIAL_BAUDRATE)):
                    vol.All(vol.Coerce(int), vol.In(SERIAL_BAUDRATES)),

            vol.Required(
                "bytesize",
                default=get_config("bytesize", DEFAULT_SERIAL_BYTESIZE)):
                    vol.All(vol.Coerce(int), vol.In(SERIAL_BYTESIZES)),

            vol.Required(
                "parity",
                default=get_config("parity", DEFAULT_PARITY)):
                    vol.All(vol.Coerce(str), vol.In(SERIAL_PARITIES)),

            vol.Required(
                "stopbits",
                default=get_config("stopbits", DEFAULT_STOPBITS)):
                    vol.All(vol.Coerce(int), vol.In(SERIAL_STOPBITS)),
        })
    elif type in ("tcp", "udp", "rtuovertcp"):
        return vol.Schema({
            # Host + Port settings
            vol.Required(
                "host",
                default=get_config("host")): str,

            vol.Required(
                "port",
                default=get_config("port", 502)):
                    vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),

        })
    else:
        return vol.Schema({
            vol.Required("name", default=get_config("name", "")): str,

            # Settings
            vol.Required(
                "response_timeout",
                default=get_config("response_timeout", DEFAULT_RESPONSE_TIMEOUT)):
                    vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),

            vol.Required(
                "modbus_type",
                default=get_config("modbus_type", DEFAULT_MODBUS_TYPE)):
                    vol.All(vol.Coerce(str), vol.In(MODBUS_TYPES)),
        })


def check_user_input(user_input):
    errors = {}
    # if user_input is not None:
    #     exp_min = user_input["wda_exp_min"]
    #     exp_max = user_input["wda_exp_max"]

    #     if exp_min > exp_max:
    #         errors["base"] = "exp_min_must_be_less"
    #         errors["wda_exp_min"] = "exp_min_must_be_less"
    return errors


class ECAdapterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ Handle a config flow for Weather Dependent Automation Sensor. """

    VERSION = 1

    def __init__(self):
        self.config_data = {}
        self.next_step = None

    async def async_step_user(self, user_input=None):
        """ Handle the initial step. """
        if self.next_step:
            return await self.next_step(user_input)

        _LOGGER.warning("Request to create config (init step): %s", user_input)

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
        _LOGGER.warning("Request to create config (connection step): %s", user_input)

        errors = {}
        if user_input is not None:
            self.config_data.update(user_input)
            errors = check_user_input(self.config_data)
            if not errors:
                return self.async_create_entry(
                    title=self.config_data["name"],
                    data=self.config_data)

        schema = await create_schema(
            hass=self.hass,
            user_input=user_input,
            type=self.config_data["modbus_type"])
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ECAdapterOptionsFlow(config_entry)


class ECAdapterOptionsFlow(config_entries.OptionsFlow):
    """ Handle options flow. """

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.config_data = {}
        self.next_step = None

    async def async_step_init(self, user_input=None):
        """ Manage the options. """
        if self.next_step:
            return await self.next_step(user_input)

        _LOGGER.warning("Request to update options (init step): %s", user_input)

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
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors
        )

    async def async_step_connection(self, user_input=None):
        """ Handle the connection step. """
        _LOGGER.warning("Request to update options (connection step): %s", user_input)

        errors = {}
        if user_input is not None:
            self.config_data.update(user_input)
            errors = check_user_input(self.config_data)
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
            type=self.config_data["modbus_type"])
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors
        )
