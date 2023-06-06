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

    def __init__(self, spi: int, sck: int, mosi: int, miso: int, csn: int, ce: int,
                 channel: int = 100, power=POWER_3, speed=SPEED_250K):
        self.spi = SPI(spi, sck=Pin(sck), mosi=Pin(mosi),
                       miso=Pin(miso), baudrate=50000)
        print(self.spi)

        self.csn = Pin(csn, mode=Pin.OUT)
        self.ce = Pin(ce, mode=Pin.OUT)

        self.nrf = NRF24L01(self.spi, self.csn,
                            self.ce, channel=channel, payload_size=32)

        self.nrf.set_power_speed(power, speed)

    def send(self, data: bytes):
        self.nrf.open_tx_pipe(self.addresses[0])
        self.nrf.open_rx_pipe(1, self.addresses[1])

        try:
            self.nrf.send_start(data)
        except:
            print(f"error sending {data}")

    def receive(self, timeout_ms: int = 100) -> list[bytes]:
        result = []

        self.nrf.open_tx_pipe(self.addresses[1])
        self.nrf.open_rx_pipe(1, self.addresses[0])

        self.nrf.start_listening()
        deadline = utime.ticks_add(utime.ticks_ms(), timeout_ms)

        while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
            if self.nrf.any():
                while self.nrf.any():
                    data = self.nrf.recv()
                    result.append(data)

        self.nrf.stop_listening()

        return result
