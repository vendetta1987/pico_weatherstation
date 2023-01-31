import ustruct as struct
import utime
from machine import SPI, Pin

from NRF24L01 import NRF24L01, POWER_3, SPEED_250K
from Weatherstation import WeatherStation


class NRFManager:
    # 57 == ASCII W; 77 == ASCII w
    addresses = (b"\x57\x57\x57\x57\x57", b"\x77\x77\x77\x77\x77")

    def __init__(self):
        self.spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
        self.cfg = {"spi": self.spi, "csn": 5, "ce": 6}

        self.csn = Pin(self.cfg["csn"], mode=Pin.OUT)
        self.ce = Pin(self.cfg["ce"], mode=Pin.OUT)

        self.nrf = NRF24L01(self.cfg["spi"], self.csn,
                            self.ce, channel=100, payload_size=32)
        self.nrf.set_power_speed(POWER_3, SPEED_250K)
        print(self.spi)

        self.nrf.open_tx_pipe(self.addresses[0])
        self.nrf.open_rx_pipe(1, self.addresses[1])


if __name__ == "__main__":
    mngr = NRFManager()
    ws = WeatherStation()

    while True:
        millis = utime.ticks_ms()
        try:
            bin = ws.Serialize()
            mngr.nrf.send(bin)
        except OSError:
            pass
        else:
            print("sending "+str(bin))

        utime.sleep_ms(100)
