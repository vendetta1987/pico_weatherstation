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
        utime.sleep_ms(1000*60)


def ContinouslyReadSensors():
    ws = WeatherStation()

    while True:
        print(f"Temperature={ws.Temperature} Humidity={ws.Humidity} Pressure={ws.Pressure} WindDirection={ws.WindDirection} WindSpeed={ws.WindSpeed} Rain={ws.Rain} SoilTemperature={ws.SoilTemperature} SoilMoisture={ws.SoilMoisture}")
        utime.sleep_ms(3000)


if __name__ == "__main__":
    SendSensorReadingsByNRF()
    #ContinouslyReadSensors()
