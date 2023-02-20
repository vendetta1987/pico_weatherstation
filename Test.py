import utime

from DS15901.TriggerCounter import TriggerCounter
from DS15901.WindVane import WindVane
from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation


def SendSensorReadingsByNRF():
    ws = WeatherStation()
    nrf_mngr = NRFManager()

    while True:
        data = ws.Serialize()
        print(f"sending {data}")
        nrf_mngr.send(data)
        utime.sleep_ms(250)


def ReadTriggers():
    anemometer = TriggerCounter(2.4, 15)
    rain_gauge = TriggerCounter(0.2794, 14)
    while True:
        utime.sleep(3)
        speed_kmh = anemometer.ReadAndResetValue()
        rain_mm = rain_gauge.ReadAndResetValue()
        print(f"wind speed={speed_kmh} mm of rain={rain_mm}")


def ReadADC():
    wv = WindVane(26)
    wv.StartMeasurements()


if __name__ == "__main__":
    # SendSensorReadingsByNRF()
    # ReadTriggers()
    ReadADC()
