import utime

from DS15901.TriggerCounter import TriggerCounter
from DS15901.WindVane import WindVane


def ReadTriggers():
    anemometer = TriggerCounter(2.4, 22, True)
    rain_gauge = TriggerCounter(0.2794, 16, False)
    while True:
        utime.sleep(3)
        speed_kmh = anemometer.EvaluatedCount
        rain_mm = rain_gauge.EvaluatedCount
        print(f"wind speed={speed_kmh} mm of rain={rain_mm}")


def ReadWindVane():
    wv = WindVane(26)

    while True:
        print(wv.Direction)
        utime.sleep_ms(500)


if __name__ == "__main__":
    ReadTriggers()
    #ReadWindVane()
