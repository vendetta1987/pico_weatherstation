import utime

from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation
from DS15901.TriggerCounter import TriggerCounter


def SendSensorReadingsByNRF():
    ws = WeatherStation()
    nrf_mngr = NRFManager()

    while True:
        data = ws.Serialize()
        print(f"sending {data}")
        nrf_mngr.send(data)
        utime.sleep_ms(250)


def SetupAndWaitForInterrupt():
    tc = TriggerCounter(3, 2.4, 15)
    while True:
        utime.sleep(tc.measurement_time_sec)
        speed_kmh = tc.ReadAndResetValue()
        print(f"wind speed={speed_kmh}")


if __name__ == "__main__":
    # SendSensorReadingsByNRF()
    SetupAndWaitForInterrupt()
