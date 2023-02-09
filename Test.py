import utime

from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation

if __name__ == "__main__":
    ws = WeatherStation()
    nrf_mngr = NRFManager()

    while True:
        data = ws.Serialize()
        print(f"sending {data}")
        nrf_mngr.send(data)
        utime.sleep_ms(250)
