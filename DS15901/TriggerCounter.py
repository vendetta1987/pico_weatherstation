from machine import Pin


class TriggerCounter:
    _trigger_count: int = 0
    measurement_time_sec: int
    _per_trigger_multi: float
    _pin: Pin

    def __init__(self, measurement_time_sec: int, per_trigger_multi: float, pin_number: int):
        self.measurement_time_sec = measurement_time_sec
        self._per_trigger_multi = per_trigger_multi

        self._pin = Pin(pin_number, Pin.IN, Pin.PULL_DOWN)
        self._pin.irq(handler=self._callback, trigger=Pin.IRQ_RISING)

    def ReadAndResetValue(self):
        tmp = self._trigger_count
        self._trigger_count = 0

        tmp = tmp/self.measurement_time_sec*self._per_trigger_multi
        return tmp

    def _callback(self, pin: Pin):
        self._trigger_count = self._trigger_count+1
