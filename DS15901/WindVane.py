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
    _adc: ADC
    _direction_count: int = 16

    def __init__(self, pin: int):
        self._adc = ADC(pin)

    def GetWindDirection(self) -> str:
        adc_value = self._adc.read_u16()

        for idx in range(self._direction_count):
            if adc_value < LIMITS[idx]:
                return DIRECTIONS[idx]

        return "unkown"
