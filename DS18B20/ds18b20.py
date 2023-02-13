import time

import onewire
from machine import Pin

import ds18x20

pin = Pin(0)
ds = ds18x20.DS18X20(onewire.OneWire(pin))

roms = ds.scan()
print(f"roms={roms}")

while True:
    ds.convert_temp()
    time.sleep_ms(750)

    for rom in roms:
        print(f"t={ds.read_temp(rom)}")

