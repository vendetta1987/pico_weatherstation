import RPi.GPIO as GPIO
import time

#https://pinout.xyz/pinout/wiringpi#
#https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/

recPinNr=7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(recPinNr, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    res=GPIO.input(recPinNr)
    print(f"received {res}")
    time.sleep(0.1)

GPIO.cleanup()