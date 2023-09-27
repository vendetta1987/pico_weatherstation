from machine import ADC

DIRECTIONS = (
    "ESE",
    "ENE",
    "E",
    "SSE",
    "SE",
    "SSW",
    "S",
    "NNE",
    "NE",
    "WSW",
    "SW",
    "NNW",
    "N",
    "WNW",
    "NW",
    "W"
)

LIMITS = (
    9350,
    10913,
    13174,
    17766,
    23293,
    27698,
    33600,
    39480,
    44922,
    49387,
    51751,
    55073,
    57558,
    59413,
    61435,
    65536
)


class WindVane:
    _DEFAULT_DIRECTION: str = "X"

    _sensor: ADC
    _direction_count: int = 16
    _histogram: dict[str, int]

    def __init__(self, pin: int):
        self._sensor = ADC(pin)
        self.ResetHistogram()

    def ResetHistogram(self):
        self._histogram = {}

        for dir in DIRECTIONS:
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

        for idx in range(self._direction_count):
            if adc_value < LIMITS[idx]:
                wind_dir = DIRECTIONS[idx]

        return wind_dir
