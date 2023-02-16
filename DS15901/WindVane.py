from machine import ADC


class WindVane:
    _adc: ADC

    def __init__(self, pin: int):
        self._adc = ADC(pin)
