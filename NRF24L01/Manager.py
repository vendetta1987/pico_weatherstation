import utime
from machine import SPI, Pin

from NRF24L01.Driver import NRF24L01, POWER_3, SPEED_250K


class NRFManager:
    # RX <-> MISO
    # TX <-> MOSI
    nrf: NRF24L01

    def __init__(self, spiID: int, sck: int, mosi: int, miso: int, csn: int, ce: int,
                 channel: int = 100, power=POWER_3, speed=SPEED_250K,
                 address_send=b"WSone", address_rec=b"WStwo"):
        spi = SPI(spiID, sck=Pin(sck), mosi=Pin(mosi),
                  miso=Pin(miso), baudrate=50000)
        print(spi)

        csnPin = Pin(csn, mode=Pin.OUT)
        cePin = Pin(ce, mode=Pin.OUT)

        self.nrf = NRF24L01(spi, csnPin, cePin,
                            channel=channel, payload_size=32)

        self.nrf.set_power_speed(power, speed)

        self.nrf.open_tx_pipe(address_send)
        self.nrf.open_rx_pipe(1, address_rec)

    def send(self, data: bytes) -> bool:
        self.nrf.stop_listening()

        try:
            self.nrf.send(data)
            return True
        except:
            #print(f"error sending {data}")
            return False

    def receive(self, timeout_ms: int = 100) -> list[bytes]:
        received_data = False
        result = []
        deadline = utime.ticks_add(utime.ticks_ms(), timeout_ms)

        self.nrf.start_listening()

        while not received_data and (utime.ticks_diff(deadline, utime.ticks_ms()) > 0):
            if self.nrf.any():
                while self.nrf.any():
                    data = self.nrf.recv()
                    result.append(data)
                received_data = True

        self.nrf.stop_listening()

        return result
