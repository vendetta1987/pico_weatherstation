import utime

from BME280.Manager import BMEManager

if __name__ == "__main__":
    bme_mngr = BMEManager(0, 2, 3, 4, 1)

    while True:
        print(f"t={bme_mngr._sensor.temperature} h={bme_mngr._sensor.humidity} p={bme_mngr._sensor.pressure} alt={bme_mngr._sensor.altitude}")
        utime.sleep_ms(100)
