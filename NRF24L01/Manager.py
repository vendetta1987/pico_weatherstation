import utime
from machine import SPI, Pin

from NRF24L01.Driver import NRF24L01, POWER_3, SPEED_250K


class NRFManager:
    # RX <-> MISO
    # TX <-> MOSI

    # letter -> ASCII -> hex
    # hex(ord("W"))
    # hex(ord("w"))
    addresses = (b"\x57\x57\x57\x57\x57", b"\x77\x77\x77\x77\x77")
    spi: SPI
    csn: Pin
    ce: Pin
    nrf: NRF24L01

    def __init__(self, spi:int, sck: int, mosi: int, miso: int, csn: int, ce: int):
        self.spi = SPI(spi, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso), baudrate=50000)
        print(self.spi)

        self.csn = Pin(csn, mode=Pin.OUT)
        self.ce = Pin(ce, mode=Pin.OUT)

        self.nrf = NRF24L01(self.spi, self.csn,
                            self.ce, channel=100, payload_size=32)

        self.nrf.set_power_speed(POWER_3, SPEED_250K)
        self.nrf.open_tx_pipe(self.addresses[0])
        self.nrf.open_rx_pipe(1, self.addresses[1])

    def send(self, data: bytes):
        try:
            self.nrf.send_start(data)
        except:
            print(f"error sending {data}")
