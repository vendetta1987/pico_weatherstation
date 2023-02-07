import utime
from adafruit_bme280.basic import Adafruit_BME280, SPI_Impl
from machine import SPI, Pin


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


if __name__ == "__main__":
    # SCL -> SCK
    # SDO -> MISO/RX
    # SDA -> MOSI/TX
    # CSB -> CSn
    spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
    csn = Pin(1, mode=Pin.OUT)

    spi_impl = PicoSPI_Impl(spi, csn)
    bme = Adafruit_BME280(spi_impl)

    bme.sea_level_pressure = 1042
    while True:
        print(f"t={bme.temperature} h={bme.humidity} h rel={bme.relative_humidity} p={bme.pressure} alt={bme.altitude}")
        utime.sleep_ms(100)
