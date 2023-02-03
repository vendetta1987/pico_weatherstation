from machine import SPI, Pin
from adafruit_bmp280 import Adafruit_BMP280

class MyBMP(Adafruit_BMP280):
    def __init__(self, spi: SPI, cs: Pin) -> None:
        self._spi = spi
        self._cs=cs
        super().__init__()

    def _read_register(self, register: int, length: int) -> bytearray:
        """Low level register reading over SPI, returns a list of values"""
        register = (register | 0x80) & 0xFF  # Read single, bit 7 high.
        self._cs.high()
        # pylint: disable=no-member
        self._spi.write(bytearray([register]))
        result = bytearray(length)
        self._spi.readinto(result)
        # print("$%02X => %s" % (register, [hex(i) for i in result]))
        self._cs.low()
        return result

    def _write_register_byte(self, register: int, value: int) -> None:
        """Low level register writing over SPI, writes one 8-bit value"""
        register &= 0x7F  # Write, bit 7 low.
        self._cs.high()
        # pylint: disable=no-member
        self._spi.write(bytes([register, value & 0xFF]))
        self._cs.low()

if __name__ == "__main__":
    # SCL -> SCK
    # SDO -> MISO/RX
    # SDA -> MOSI/TX
    # CSB -> CSn
    spi = SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12))
    csn = Pin(13, mode=Pin.OUT)

    bmp = Adafruit_BMP280_SPI(spi, csn)
    print(bmp.temperature)
