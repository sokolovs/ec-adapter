""" Sensor converters """
import datetime

from homeassistant.util import dt as ha_dt


def uptime_to_boottime(uptime: int):
    return ha_dt.now() - datetime.timedelta(seconds=uptime)
