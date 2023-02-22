import onewire
from ds18x20 import DS18X20
from machine import Pin


class DS18B20Manager:
    _sensor: DS18X20
    _devices: list

    def __init__(self, pin: int):
        _pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        ow = onewire.OneWire(_pin)
        self._sensor = DS18X20(ow)
        self._devices = self._sensor.scan()
        print(f"devices={self._devices}")

    def GetTemperature(self) -> float:
        for device in self._devices:
            print(f"device {device}={self._sensor.read_temp(device)}")

        return 0.0
