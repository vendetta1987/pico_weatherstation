import time
from DS18B20.Manager import DS18B20Manager

if __name__ == "__main__":
    ds_mngr = DS18B20Manager(13)
    while True:
        ds_mngr.GetTemperature()
        time. sleep_ms(500)