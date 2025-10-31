import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .helpers import create_modbus_client
from .registers import REGISTERS, REG_DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ModbusCoordinator(DataUpdateCoordinator):
    """ Modbus data updater """

    def __init__(
            self,
            hass: HomeAssistant,
            config_entry,
            registers,
            scan_interval=REG_DEFAULT_SCAN_INTERVAL):

        if not set(registers).issubset(REGISTERS.keys()):
            error = "Unwnown registers found in: %s" % registers
            _LOGGER.error(error)
            raise Exception(error)

        self.registers = registers
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval))

        self.config = config_entry.data.copy()
        self.config.update(config_entry.options)
        self.client = None

    async def _connect(self):
        try:
            self.client = create_modbus_client(self.config)
            result = await self.client.connect()
            if not result:
                _LOGGER.error("Failed to connect to Modbus device")
        except Exception as ex:
            _LOGGER.error("Error connecting to Modbus: %s", ex)

    async def _async_update_data(self):
        if not self.client or not self.client.connected:
            await self._connect()
            if not self.client.connected:
                raise Exception("Modbus device not connected")

        data = {}
        try:
            for register in self.registers:
                result = await self.client.read_holding_registers(
                    address=register,
                    count=REGISTERS[register]["count"])
                if result.isError():
                    _LOGGER.error("Modbus read error")
                    data[register] = None
                data[register] = result.registers
        except Exception as e:
            _LOGGER.error("Modbus exception while read: %s", e)
        finally:
            if self.client:
                self.client.close()
        return data
