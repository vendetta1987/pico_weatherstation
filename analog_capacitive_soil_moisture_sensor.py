import time

from machine import ADC

adc = ADC(2)

while True:
    print(f"{adc.read_u16()}")
    time.sleep_ms(500)
