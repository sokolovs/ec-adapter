import asyncio
import logging
from typing import Any, Dict, List

from .const import QUEUE_TIMEOUT
from .helpers import create_modbus_client
from .registers import (
    REG_DEFAULT_MAX_RETRIES,
    REG_DEFAULT_RETRY_DELAY,
    REG_STATUS_OFFSET,
    REG_STATUS_OK
)

_LOGGER = logging.getLogger(__name__)


class ModbusMasterCoordinator:
    """ Main coordinator for managing all Modbus operations """

    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry

        self._config = config_entry.data.copy()
        self._config.update(config_entry.options)

        self._client = None
        self._queue = asyncio.Queue()
        self._processing_task = None
        self._is_running = False
        self._current_operation = None
        self._operation_lock = asyncio.Lock()

    async def async_start(self):
        self._is_running = True
        self._processing_task = asyncio.create_task(self._process_queue())
        _LOGGER.info("Modbus master coordinator: STARTED")

    async def async_stop(self):
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

        _LOGGER.info("Modbus master coordinator: STOPPED")

    async def _connect(self):
        """ Connecto to Modbus slave """
        try:
            self._client = create_modbus_client(self._config)
            result = await self._client.connect()
            if not result:
                _LOGGER.error("Failed to connect to Modbus device")
        except Exception as e:
            _LOGGER.error(f"Error connecting to Modbus: {e}")

    async def _get_modbus_client(self):
        """ Rreturn connected Modbus client """
        if not self._client or not self._client.connected:
            await self._connect()
            if not self._client.connected:
                raise Exception("Modbus device not connected")
        return self._client

    async def _process_queue(self):
        """ The main loop for processing Modbus commands """
        while self._is_running:
            try:
                operation_id, operation_type, operation_data, future = await asyncio.wait_for(
                    self._queue.get(), timeout=QUEUE_TIMEOUT)

                async with self._operation_lock:
                    self._current_operation = operation_id
                    try:
                        result = await self._execute_operation(operation_type, operation_data)
                        if not future.done():
                            future.set_result(result)
                    except Exception as e:
                        if not future.done():
                            future.set_exception(e)
                        _LOGGER.error(f"Operation {operation_id} failed: {e}")
                    finally:
                        self._current_operation = None
                        self._queue.task_done()

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.error(f"Unexpected error in queue processing: {e}")

    async def _execute_operation(self, op: str, data: Dict[str, Any]):
        """ Backend for execute same operation """
        client = await self._get_modbus_client()

        try:
            if op == "read_holding_registers":
                return await client.read_holding_registers(
                    address=data["address"],
                    count=data["count"],
                    device_id=self._config["slave"]
                )
            elif op == "write_registers":
                result = await client.write_registers(
                    address=data["address"],
                    values=data["values"],
                    device_id=self._config["slave"]
                )

                status_register = (
                    data["status_register"] or
                    data["address"] + REG_STATUS_OFFSET
                )

                success = await self._verify_write_status(
                    status_register,
                    data.get("success_status", REG_STATUS_OK),
                    data.get("max_retries", REG_DEFAULT_MAX_RETRIES),
                    data.get("retry_delay", REG_DEFAULT_RETRY_DELAY)
                )
                return (success and result)
            else:
                raise ValueError(f"Unknown operation type: {op}")

        except Exception as e:
            _LOGGER.error(f"Error executing '{op}' operation: {e}")

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
                if result is not None:
                    if result.isError():
                        _LOGGER.error(f"Modbus read status register={status_register:#06x} error")
                    elif len(result.registers) and result.registers[0] == success_status:
                        return True
            except Exception as e:
                _LOGGER.error(f"Attempt {attempt + 1} failed to read status register: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)

        return False

    async def read_holding_registers(self, address: int, count: int) -> Any:
        return await self._submit_operation(
            "read_holding_registers", {"address": address, "count": count})

    async def write_registers(self, address: int, values: List[int], status_register=None) -> bool:
        return await self._submit_operation(
            "write_registers", {"address": address, "values": values, "status_register": status_register})

    async def _submit_operation(self, op: str, data: Dict[str, Any]):
        """ Adds a operation to the queue and waits for the result """
        if not self._is_running:
            raise RuntimeError("Modbus coordinator is not running")

        operation_id = f"{op}_{id(data)}"
        future = asyncio.Future()

        await self._queue.put((operation_id, op, data, future))
        return await future

    @property
    def current_operation(self) -> str:
        """ Return current operation ID """
        return self._current_operation

    @property
    def queue_size(self) -> int:
        """ Current queue size """
        return self._queue.qsize()
