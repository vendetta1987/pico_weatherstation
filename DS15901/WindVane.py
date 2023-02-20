import uasyncio
from machine import ADC

direction_lut = {
    1: "E",
    4: "SE",
    6: "S",
    10: "NE",
    12: "W",
    14: "N",
    15: "NW"
}


class WindVane:
    _adc: ADC
    _histogram: list
    _continue_measure: bool
    _direction_count: int = 16

    def __init__(self, pin: int):
        self._adc = ADC(pin)
        self._histogram = [0]*self._direction_count

    def StartMeasurements(self):
        self._continue_measure = True

        uasyncio.create_task(self.Evaluate())
        uasyncio.run(self.Measure())

    async def Measure(self):
        min_value = 65536
        max_value = 0

        while self._continue_measure:
            adc_value = self._adc.read_u16()

            min_value = min(min_value, adc_value)
            max_value = max(max_value, adc_value)

            # print(f"min={min_value}\tmax={max_value}\tadc={adc_value}")

            if max_value > min_value:
                diff = max_value-min_value
                window = (adc_value-min_value)/diff
                idx = round(window*self._direction_count)

                if 0 <= idx < self._direction_count:
                    self._histogram[idx] += 1

            await uasyncio.sleep_ms(100)

    async def Evaluate(self):
        while True:
            await uasyncio.sleep(2)
            max_value = max(self._histogram)

            if max_value > 0:
                for i in range(self._direction_count):
                    bar = "#"*int(self._histogram[i]/max_value*25)
                    print(f"{i}\t"+bar)

            self._histogram = [0]*self._direction_count
