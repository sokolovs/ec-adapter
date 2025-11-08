import asyncio
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, W_QUEUE_TIMEOUT
from .helpers import create_modbus_client
from .registers import (
    REGISTERS_R,
    REGISTERS_W,
    REG_DEFAULT_MAX_RETRIES,
    REG_DEFAULT_RETRY_DELAY,
    REG_DEFAULT_SCAN_INTERVAL,
    REG_STATUS_OFFSET,
    REG_STATUS_OK
)

_LOGGER = logging.getLogger(__name__)


class ModbusReadCoordinator(DataUpdateCoordinator):
    """ Modbus data updater """

    def __init__(
            self,
            hass: HomeAssistant,
            config_entry,
            registers,
            scan_interval=REG_DEFAULT_SCAN_INTERVAL):

        self.registers = [addr for addr, config in registers]
        if not set(self.registers).issubset(REGISTERS_R.keys()):
            error = "Unwnown registers found in: %s" % registers
            _LOGGER.error(error)
            raise ValueError(error)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval))

        self._config = config_entry.data.copy()
        self._config.update(config_entry.options)
        self._client = None

    async def _connect(self):
        try:
            self._client = create_modbus_client(self._config)
            result = await self._client.connect()
            if not result:
                _LOGGER.error("Failed to connect to Modbus device")
        except Exception as ex:
            _LOGGER.error("Error connecting to Modbus: %s", ex)

    async def _async_update_data(self):
        if not self._client or not self._client.connected:
            await self._connect()
            if not self._client.connected:
                raise Exception("Modbus device not connected")

        data = {}
        try:
            for register in self.registers:
                result = await self._client.read_holding_registers(
                    address=register,
                    count=REGISTERS_R[register]["count"],
                    device_id=self._config["slave"])
                if result.isError():
                    _LOGGER.error("Modbus read error")
                    data[register] = None
                data[register] = result.registers
        except Exception as e:
            _LOGGER.error("Modbus exception while read: %s", e)
        finally:
            if self._client:
                self._client.close()
        return data


class ModbusWriteCoordinator:
    """ Modbus data writer """

    def __init__(self, hass: HomeAssistant, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self._config = config_entry.data.copy()
        self._config.update(config_entry.options)
        self._client = None
        self._write_queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def async_start(self):
        """ Start queue handler """
        self._is_running = True
        self._processing_task = asyncio.create_task(self._process_write_queue())
        _LOGGER.debug("Modbus write coordinator: STARTED")

    async def async_stop(self):
        """ Stop queue handler """
        self._is_running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None

        # Close Modbus connection
        if self._client:
            self._client.close()

        _LOGGER.debug("Modbus write coordinator STOPPED")

    async def _connect(self):
        try:
            self._client = create_modbus_client(self._config)
            result = await self._client.connect()
            if not result:
                _LOGGER.error("Failed to connect to Modbus device")
        except Exception as ex:
            _LOGGER.error("Error connecting to Modbus: %s", ex)

    async def _get_modbus_client(self):
        """ Rreturn connected modbus client """
        if not self._client or not self._client.connected:
            await self._connect()
            if not self._client.connected:
                raise Exception("Modbus device not connected")
        return self._client

    async def _process_write_queue(self):
        """ The main loop for processing write commands """
        while self._is_running:
            try:
                try:
                    operation_id, register, values, future = await asyncio.wait_for(
                        self._write_queue.get(), timeout=W_QUEUE_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    continue

                try:
                    result = await self._execute_write_operation(register, values)
                    if not future.done():
                        future.set_result(result)
                except Exception as e:
                    if not future.done():
                        future.set_exception(e)
                finally:
                    self._write_queue.task_done()

            except asyncio.CancelledError:
                _LOGGER.debug("Write queue processor received cancellation")
                break
            except Exception as e:
                _LOGGER.error("Unexpected error in write queue processing: %s", e)

    async def _execute_write_operation(self, register: int, values: list[int]) -> bool:
        """ Performs a write operation with status checking """
        client = await self._get_modbus_client()

        try:
            await client.write_registers(
                address=register,
                values=values,
                device_id=self._config["slave"])

            # Check write status
            success = await self._verify_write_status(
                register + REG_STATUS_OFFSET,
                REGISTERS_W[register].get("success_status", REG_STATUS_OK),
                REGISTERS_W[register].get("max_retries", REG_DEFAULT_MAX_RETRIES),
                REGISTERS_W[register].get("retry_delay", REG_DEFAULT_RETRY_DELAY)
            )
            return success

        except Exception as e:
            _LOGGER.error("Error executing write operation: %s", e)

        return False

    async def _verify_write_status(
            self,
            status_register: int,
            success_status: int,
            max_retries: int,
            retry_delay: float) -> bool:
        """ Checks write status """
        client = await self._get_modbus_client()

        for attempt in range(max_retries):
            try:
                result = await client.read_holding_registers(
                    address=status_register,
                    device_id=self._config["slave"])
                if result.isError():
                    _LOGGER.error(f"Modbus read status register={status_register:#06x} error")
                elif len(result.registers) and result.registers[0] == success_status:
                    return True
            except Exception as e:
                _LOGGER.error(f"Attempt {attempt + 1} failed to read status register: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)

        return False

    async def submit_write_operation(self, register, values: list[int]) -> bool:
        """ Adds a write operation to the queue and waits for the result """
        if not self._is_running:
            raise RuntimeError("Write manager is not running")

        operation_id = f"{register}_{values}"
        future = asyncio.Future()

        await self._write_queue.put((operation_id, register, values, future))

        # Wait for the result
        return await future

    @property
    def queue_size(self) -> int:
        """ Current queue size """
        return self._write_queue.qsize()
