import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .master import ModbusMasterCoordinator
from .registers import REGISTERS_R, REG_DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ModbusDataUpdateCoordinator(DataUpdateCoordinator):
    """ Modbus data updater """

    def __init__(
            self,
            hass: HomeAssistant,
            config_entry,
            master: ModbusMasterCoordinator,
            registers,
            scan_interval=REG_DEFAULT_SCAN_INTERVAL):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval))
        self.hass = hass
        self.config_entry = config_entry
        self._config = config_entry.options or config_entry.data
        self._master = master

        self._registers = [addr for addr, config in registers]
        if not set(self._registers).issubset(REGISTERS_R.keys()):
            error = f"Unwnown registers found in: {self._registers}"
            _LOGGER.error(error)
            raise ValueError(error)

    async def _async_update_data(self):
        data = {}
        try:
            for register in self._registers:
                result = await self._master.read_holding_registers(
                    address=register,
                    count=REGISTERS_R[register]["count"])
                if result is None or result.isError():
                    _LOGGER.error("Modbus read error")
                    data[register] = None
                else:
                    data[register] = result.registers
        except Exception as e:
            raise UpdateFailed(f"Exception while Modbus read: {e}")
        return data
