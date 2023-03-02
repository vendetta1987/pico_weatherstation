import time

from CAPSHYG.Manager import SoilMoistureManager

if __name__ == "__main__":
    sm = SoilMoistureManager(27)
    while True:
        print(f"{sm.Moisture} cm^3/cm^3")
        time.sleep_ms(500)
