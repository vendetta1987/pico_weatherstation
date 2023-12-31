import utime

from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation
from machine import Pin


def SendSensorReadingsByNRF():
    ws = WeatherStation()
    nrf_mngr = NRFManager(0, 2, 3, 4, 0, 6)

    while True:
        packets = ws.Serialize()
        for packet in packets:
            print(f"sending {packet}")
            nrf_mngr.send(packet)
            utime.sleep_ms(10)
        utime.sleep_ms(250)


def ContinouslyReadSensors():
    ws = WeatherStation()

    while True:
        ws.Update()
        print(f"Temperature={ws.Temperature} Humidity={ws.Humidity} Pressure={ws.Pressure} WindDirection={ws.WindDirection} WindSpeed={ws.WindSpeed} Rain={ws.Rain} SoilTemperature={ws.SoilTemperature} SoilMoisture={ws.SoilMoisture}")
        utime.sleep_ms(3000)


def ContinousSendingTest():
    nrf_mngr = NRFManager(0, 2, 3, 4, 0, 6)

    i = 0
    while True:
        print(f"sending.. {i}")
        i += 1
        nrf_mngr.send(b"test")
        utime.sleep_ms(200)


def WakeupTest():
    nrf_mngr = NRFManager(0, 2, 3, 4, 0, 6)

    print("waiting for wakeup")
    while True:
        data = nrf_mngr.receive(1000)

        for packet in data:
            if "wake_up" in str(packet):
                print("signaling awake")
                nrf_mngr.send(b"im awake")
                utime.sleep_ms(10)


def ReceivedWakeupCall():
    global nrf_mngr

    data = nrf_mngr.receive(1000)

    for packet in data:
        if "wake_up" in str(packet):
            return True

    return False


if __name__ == "__main__":
    # SendSensorReadingsByNRF()
    # ContinouslyReadSensors()
    # ContinousSendingTest()
    # WakeupTest()

    led = Pin(25, Pin.OUT)
    led.off()

    nrf_mngr = NRFManager(0, 2, 3, 4, 0, 6)
    ws = WeatherStation()

    while True:
        ws.Update()

        if ReceivedWakeupCall():
            led.on()
            packets = ws.Serialize()

            for i in range(10):
                print(f"sending data, try {i}")
                for packet in packets:
                    nrf_mngr.send(packet)

            ws.Reset()

        led.off()
        utime.sleep(3)


