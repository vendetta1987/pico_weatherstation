import utime

from BME280.Manager import BMEManager

if __name__ == "__main__":
    bme_mngr = BMEManager()
    bme_mngr.bme.sea_level_pressure = 1042

    while True:
        print(f"t={bme_mngr.bme.temperature} h={bme_mngr.bme.humidity} p={bme_mngr.bme.pressure} alt={bme_mngr.bme.altitude}")
        utime.sleep_ms(100)
