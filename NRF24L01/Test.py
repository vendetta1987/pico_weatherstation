import random

import ustruct as struct
import utime
from machine import ADC

from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation


def GetPicoTemperature():
    reading = sensor_temp.read_u16() * conversion_factor
    return 27 - (reading - 0.706)/0.001721


sensor_temp = ADC(4)
conversion_factor = 3.3 / (65535)

if __name__ == "__main__":
    nrf_mngr = NRFManager()
    ws = WeatherStation()
    cnt = 0

    while True:
        try:
            ws.Temperature = GetPicoTemperature()
            ws.Humidity = random.randrange(0, 1000)/10

            bin = ws.Serialize()
            bin = struct.pack("i", cnt)+bin

            print(
                f"sending {cnt}: t={ws.Temperature}, h={ws.Humidity} -> {str(bin)}")
            nrf_mngr.send(bin)
        except:
            print(f"error at {cnt}")

        cnt = cnt+1
        utime.sleep_ms(1000)
