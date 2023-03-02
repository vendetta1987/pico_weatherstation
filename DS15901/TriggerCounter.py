from machine import Pin
import time


class TriggerCounter:
    _trigger_count: int = 0
    _per_trigger_multi: float
    _pin: Pin
    _start_measure_time: int

    def __init__(self, per_trigger_multi: float, pin_number: int):
        self._per_trigger_multi = per_trigger_multi

        self._pin = Pin(pin_number, Pin.IN, Pin.PULL_DOWN)
        self._pin.irq(handler=self._callback, trigger=Pin.IRQ_RISING)
        self._start_measure_time = time.ticks_ms()

    @property
    def EvaluatedCount(self):
        tmp_count = self._trigger_count
        self._trigger_count = 0

        time_diff_sec = time.ticks_diff(
            time.ticks_ms(), self._start_measure_time)/1000
        self._start_measure_time = time.ticks_ms()

        calculated_value = tmp_count/time_diff_sec*self._per_trigger_multi
        return calculated_value

    def _callback(self, pin: Pin):
        self._trigger_count = self._trigger_count+1
