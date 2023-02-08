from machine import SPI, Pin

from BME280.adafruit_bme280.basic import SPI_Impl


class PicoSPI_Impl(SPI_Impl):
    def __init__(self, spi: SPI, cs: Pin) -> None:
        self._spi = spi
        self._cs = cs

    def read_register(self, register: int, length: int) -> bytearray:
        "Read from the device register."
        register = (register | 0x80) & 0xFF  # Read single, bit 7 high.
        self._cs.low()
        self._spi.write(bytearray([register]))  # pylint: disable=no-member
        result = bytearray(length)
        self._spi.readinto(result)  # pylint: disable=no-member
        self._cs.high()
        # print("$%02X => %s" % (register, [hex(i) for i in result]))
        return result

    def write_register_byte(self, register: int, value: int) -> None:
        "Write value to the device register."
        register &= 0x7F  # Write, bit 7 low.
        self._cs.low()
        self._spi.write(bytes([register, value & 0xFF]))
        self._cs.high()