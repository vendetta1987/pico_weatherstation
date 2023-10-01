from machine import ADC


class WindVane:
    _DEFAULT_DIRECTION: str = "X"
    _ADC_DIR_LUT: tuple[tuple[int, str], ...] = (
        (9350, "ESE"),
        (10913, "ENE"),
        (13174, "E"),
        (17766, "SSE"),
        (23293, "SE"),
        (27698, "SSW"),
        (33600, "S"),
        (39480, "NNE"),
        (44922, "NE"),
        (49387, "WSW"),
        (51751, "SW"),
        (55073, "NNW"),
        (57558, "N"),
        (59413, "WNW"),
        (61435, "NW"),
        (65536, "W"))

    _sensor: ADC
    _histogram: dict[str, int]

    def __init__(self, pin: int):
        self._sensor = ADC(pin)
        self.ResetHistogram()

    def ResetHistogram(self):
        self._histogram = {}

        for _, dir in WindVane._ADC_DIR_LUT:
            self._histogram[dir] = 0

    def UpdateHistogram(self):
        wind_dir = self.Direction

        if wind_dir in self._histogram:
            self._histogram[wind_dir] += 1

    @property
    def AverageDirection(self) -> str:
        if max(self._histogram.values()) > 0:
            return max(self._histogram, key=lambda k: self._histogram[k])
        else:
            return WindVane._DEFAULT_DIRECTION

    @property
    def Direction(self) -> str:
        adc_value = self._sensor.read_u16()
        wind_dir = WindVane._DEFAULT_DIRECTION

        for idx in range(len(WindVane._ADC_DIR_LUT)-1):
            if adc_value > WindVane._ADC_DIR_LUT[idx][0]:
                wind_dir = WindVane._ADC_DIR_LUT[idx+1][1]

        return wind_dir
