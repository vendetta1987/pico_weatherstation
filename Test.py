import utime

from DS15901.TriggerCounter import TriggerCounter
from NRF24L01.Manager import NRFManager
from Weatherstation import WeatherStation

import machine
from math import sqrt


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
    adc = machine.ADC(26)

    min_value = 65536
    max_value = 0
    histogram_size = 100
    histogram = [0]*histogram_size
    loop_cnt = 0

    while True:
        if (loop_cnt > 0) and ((loop_cnt % 10000) == 0):
            for i in range(len(histogram)-1):
                bar = "#"*int(histogram[i]/10)
                print(f"{i}\t"+bar)

            avg = 0
            avg_sample_cnt = 0
            for i in range(len(histogram)-1):
                if histogram[i] > 0:
                    avg += histogram[i]
                    avg_sample_cnt += 1

            if avg_sample_cnt > 0:
                avg /= avg_sample_cnt

            avg_val_idx = 0
            variance = 0

            if avg > 0:
                variance_sample_cnt = 0

                min_diff = 4096

                for i in range(len(histogram)-1):
                    if histogram[i] > 0:
                        tmp_diff = histogram[i]-avg
                        variance += pow(tmp_diff, 2)
                        variance_sample_cnt += 1

                        if 0 <= tmp_diff < min_diff:
                            min_diff = tmp_diff
                            avg_val_idx = i

                if variance_sample_cnt > 1:
                    variance /= variance_sample_cnt-1
                    variance = sqrt(variance)

                avg_val_idx = 4095-(histogram_size-avg_val_idx)

            print(
                f"adc_val={avg_val_idx} avg={avg} variance={variance} hist_size={histogram_size} min={min_value} max={max_value}")

            if max_value > min_value:
                histogram_size = max_value-min_value

            histogram = [0]*histogram_size
            loop_cnt = 0

        adc_value = (int)(adc.read_u16()/65535*4095)

        min_value = min(min_value, adc_value)
        max_value = max(max_value, adc_value)

        idx = adc_value-(4096-histogram_size)

        if 0 <= idx < len(histogram):
            histogram[idx] += 1

        loop_cnt += 1
        utime.sleep_us(10)


if __name__ == "__main__":
    # SendSensorReadingsByNRF()
    # ReadTriggers()
    ReadADC()
