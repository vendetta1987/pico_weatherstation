from machine import SPI, Pin

from BME280.adafruit_bme280.basic import Adafruit_BME280
from BME280.PicoSPI import PicoSPI_Impl


class BMEManager():
    # SCL -> SCK
    # SDO -> MISO/RX
    # SDA -> MOSI/TX
    # CSB -> CSn

    def __init__(self):
        spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
        csn = Pin(1, mode=Pin.OUT)

        spi_impl = PicoSPI_Impl(spi, csn)
        self.bme = Adafruit_BME280(spi_impl)
