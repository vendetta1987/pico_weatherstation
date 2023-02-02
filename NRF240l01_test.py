import random

import ustruct as struct
import utime
from machine import ADC, SPI, Pin

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


def GetPicoTemperature():
    reading = sensor_temp.read_u16() * conversion_factor
    return 27 - (reading - 0.706)/0.001721


sensor_temp = ADC(4)
conversion_factor = 3.3 / (65535)

if __name__ == "__main__":
    nrf_mngr = NRFManager()
    ws = WeatherStation()

    cnt = 0
    wait_cnt = 0
    while True:
        if (cnt > 0) and (nrf_mngr.nrf.send_done() is None) and (wait_cnt < 100):
            wait_cnt = wait_cnt+1
            utime.sleep_us(10)
            continue

        wait_cnt = 0
        ticks_begin = utime.ticks_ms()

        try:
            ws.Temperature = GetPicoTemperature()
            ws.Humidity = random.randrange(0, 1000)/10

            bin = ws.Serialize()
            bin = struct.pack("i", cnt)+bin

            print(
                f"sending {cnt}: t={ws.Temperature}, h={ws.Humidity} -> {str(bin)}")
            nrf_mngr.nrf.send_start(bin)
        except:
            print(f"error at {cnt}")

        cnt = cnt+1

        duration = utime.ticks_diff(utime.ticks_ms(), ticks_begin)
        print(duration)
        utime.sleep_ms(1000-duration)
