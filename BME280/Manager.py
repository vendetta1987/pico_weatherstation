import utime
from machine import SPI, Pin

from BME280.adafruit_bme280.basic import Adafruit_BME280
from BME280.PicoSPI import PicoSPI_Impl


class BMEManager():
    # SCL -> SCK
    # SDO -> MISO/RX
    # SDA -> MOSI/TX
    # CSB -> CSn

    _sensor: Adafruit_BME280

    def __init__(self, spi: int, sck: int, mosi: int, miso: int, csn: int):
        _spi = SPI(spi, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        csnPin = Pin(1, mode=Pin.OUT)
        spi_impl = PicoSPI_Impl(_spi, csnPin)

        self._sensor = Adafruit_BME280(spi_impl)
        self._sensor.sea_level_pressure = 1042

    @property
    def Temperature(self) -> float:
        # once to wake the sensor
        _ = self._sensor.temperature
        utime.sleep_ms(50)
        # average the next two readings
        val1 = self._sensor.temperature
        utime.sleep_ms(50)
        val2 = self._sensor.temperature

        return (val1+val2)/2

    @property
    def Humidity(self) -> float:
        return self._sensor.humidity

    @property
    def Pressure(self) -> float:
        return self._sensor.pressure
