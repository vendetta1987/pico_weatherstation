import utime

from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation


def SendSensorReadingsByNRF():
    ws = WeatherStation()
    nrf_mngr = NRFManager(0, 2, 3, 4, 0, 6)

    while True:
        packets = ws.Serialize()
        print(f"sending {packets}")
        for packet in packets:
            nrf_mngr.send(packet)
            utime.sleep_ms(10)
        utime.sleep_ms(250)


if __name__ == "__main__":
    SendSensorReadingsByNRF()
