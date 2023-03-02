import time
from math import nan

from ds18x20 import DS18X20
from machine import Pin
from onewire import OneWire


class DS18B20Manager:
    _sensor: DS18X20
    _devices: list

    def __init__(self, pin: int):
        _pin = Pin(pin, Pin.IN)
        self._sensor = DS18X20(OneWire(_pin))
        self._devices = self._sensor.scan()

    @property
    def Temperature(self) -> float:
        if len(self._devices) > 0:
            self._sensor.convert_temp()
            time.sleep_ms(750)
            return self._sensor.read_temp(self._devices[0])
        else:
            return nan
