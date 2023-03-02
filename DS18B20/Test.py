import time
from DS18B20.Manager import DS18B20Manager

if __name__ == "__main__":
    # remember 4.7kOhm between VCC and data line, its essential
    ds_mngr = DS18B20Manager(13)
    while True:
        print(f"{ds_mngr.Temperature}°C")
        time.sleep_ms(500)
