import utime

from BME280.Manager import BMEManager

if __name__ == "__main__":
    bme_mngr = BMEManager()
    bme_mngr.sensor.sea_level_pressure = 1042

    while True:
        print(f"t={bme_mngr.sensor.temperature} h={bme_mngr.sensor.humidity} p={bme_mngr.sensor.pressure} alt={bme_mngr.sensor.altitude}")
        utime.sleep_ms(100)
