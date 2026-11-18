import asyncio
import logging
from typing import Any, Dict, List, Tuple

from .const import (
    DATA_MASTERS,
    DOMAIN,
    MODBUS_TYPE_SERIAL,
    OPT_DEVICE,
    OPT_HOST,
    OPT_MODBUS_TYPE,
    OPT_PORT,
    OPT_SLAVE,
    QUEUE_TIMEOUT
)
from .helpers import create_modbus_client
from .registers import (
    REG_DEFAULT_MAX_RETRIES,
    REG_DEFAULT_RETRY_DELAY,
    REG_STATUS_OFFSET,
    REG_STATUS_OK
)

_LOGGER = logging.getLogger(__name__)


def _connection_key(config: Dict[str, Any]) -> Tuple[str, ...]:
    """ Unique key of a Modbus bus (all entries on one bus share one master). """
    modbus_type = config[OPT_MODBUS_TYPE]
    if modbus_type == MODBUS_TYPE_SERIAL:
        return (modbus_type, config[OPT_DEVICE])
    return (modbus_type, config[OPT_HOST], int(config[OPT_PORT]))


class ModbusMasterHandle:
    """ Per-entry view of a shared Modbus master.
    Binds the shared request queue to the slave ID of one config entry,
    so several entries on the same bus can safely share one master. """

    def __init__(self, master: "ModbusMasterCoordinator", config_entry, slave: int):
        self.config_entry = config_entry
        self._config = config_entry.options or config_entry.data
        self._master = master
        self._slave = slave

    async def read_holding_registers(self, address: int, count: int) -> Any:
        return await self._master.read_holding_registers(address, count, self._slave)

    async def write_registers(self, address: int, values: List[int], status_register=None) -> bool:
        return await self._master.write_registers(address, values, self._slave, status_register)

    async def async_release(self) -> None:
        """ Release this entry's reference to the shared master. """
        await self._master.async_release()

    @property
    def current_operation(self) -> str:
        """ Return current operation ID """
        return self._master.current_operation

    @property
    def queue_size(self) -> int:
        """ Current queue size """
        return self._master.queue_size


class ModbusMasterCoordinator:
    """ Main coordinator for managing all Modbus operations.
    Singleton per Modbus bus: one instance (and one request queue) for each
    unique connection key, shared by all config entries on that bus. """

    def __init__(self, hass, config: Dict[str, Any]):
        self.hass = hass
        self._config = config
        self.connection_key = _connection_key(config)
        self._client = None
        self._queue = asyncio.Queue()
        self._processing_task = None
        self._is_running = False
        self._current_operation = None
        self._operation_lock = asyncio.Lock()
        self._refcount = 0

    @classmethod
    async def async_acquire(cls, hass, config_entry) -> ModbusMasterHandle:
        """ Return a per-entry handle to the singleton master of the entry's bus,
        creating and starting the master on first use. """
        config = config_entry.options or config_entry.data
        key = _connection_key(config)

        masters = hass.data.setdefault(DOMAIN, {}).setdefault(DATA_MASTERS, {})
        master = masters.get(key)
        if master is None:
            master = cls(hass, config)
            masters[key] = master
            await master.async_start()
            _LOGGER.info("Modbus master created for %s", key)
        else:
            _LOGGER.debug("Reusing Modbus master for %s (refcount=%d)", key, master._refcount + 1)

        master._refcount += 1
        return ModbusMasterHandle(master, config_entry, int(config[OPT_SLAVE]))

    async def async_release(self) -> None:
        """ Drop one reference; when the last entry leaves the bus,
        stop the master and remove it from the registry. """
        if self._refcount > 0:
            self._refcount -= 1
        if self._refcount > 0:
            return

        masters = self.hass.data.get(DOMAIN, {}).get(DATA_MASTERS)
        if masters:
            masters.pop(self.connection_key, None)
        await self.async_stop()

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
            self._client = None

        _LOGGER.info("Modbus master coordinator: STOPPED")

    async def _connect(self):
        """ Connect to Modbus slave """
        try:
            self._client = create_modbus_client(self._config)
            result = await self._client.connect()
            if not result:
                _LOGGER.error("Failed to connect to Modbus device")
        except Exception as e:
            _LOGGER.error(f"Error connecting to Modbus: {e}")

    async def _get_modbus_client(self):
        """ Return connected Modbus client """
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
        slave = int(data["slave"])

        try:
            if op == "read_holding_registers":
                return await client.read_holding_registers(
                    address=data["address"],
                    count=data["count"],
                    device_id=slave
                )
            elif op == "write_registers":
                result = await client.write_registers(
                    address=data["address"],
                    values=data["values"],
                    device_id=slave
                )

                status_register = (
                    data["status_register"] or
                    data["address"] + REG_STATUS_OFFSET
                )

                success = await self._verify_write_status(
                    status_register,
                    data.get("success_status", REG_STATUS_OK),
                    data.get("max_retries", REG_DEFAULT_MAX_RETRIES),
                    data.get("retry_delay", REG_DEFAULT_RETRY_DELAY),
                    slave
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
            retry_delay: float,
            slave: int) -> bool:
        """ Checks write status """
        client = await self._get_modbus_client()

        for attempt in range(max_retries):
            try:
                result = await client.read_holding_registers(
                    address=status_register,
                    device_id=slave)
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

    async def read_holding_registers(self, address: int, count: int, slave: int) -> Any:
        return await self._submit_operation(
            "read_holding_registers", {"address": address, "count": count, "slave": slave})

    async def write_registers(
            self, address: int, values: List[int], slave: int, status_register=None) -> bool:
        return await self._submit_operation(
            "write_registers",
            {"address": address, "values": values, "slave": slave, "status_register": status_register})

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
