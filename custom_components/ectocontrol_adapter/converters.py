""" Sensor converters """
import datetime

from homeassistant.util import dt as ha_dt


def uptime_to_boottime(uptime: int):
    boottime = ha_dt.now() - datetime.timedelta(seconds=uptime)
    return boottime.replace(second=0, microsecond=0)
