from machine import ADC


class SoilMoistureManager:
    _sensor: ADC
    _slope: float = 2.48
    _intercept: float = -0.72

    def __init__(self, pin: int):
        self._sensor = ADC(pin)

    @property
    def Moisture(self) -> float:
        raw = self._sensor.read_u16()
        #print(f"raw={raw}")
        raw = raw/65536*3.3
        return ((1.0/raw)*self._slope)+self._intercept
