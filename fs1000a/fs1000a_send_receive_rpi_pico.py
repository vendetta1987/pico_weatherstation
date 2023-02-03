import _thread
import utime
from machine import Pin
#from rfsocket import RFSocket

#https://docs.micropython.org/en/latest/rp2/quickref.html#pins-and-gpio
#https://www.instructables.com/Super-Simple-Raspberry-Pi-433MHz-Home-Automation/

recPin = Pin(0, mode=Pin.IN)
senPin = Pin(1, mode=Pin.OUT)
#socket = RFSocket(recPin)


def send():
    while True:
        senPin.toggle()
        print(f"\tsending: {senPin.value()}")
        utime.sleep(1)


recPin.init()
recPin.off()
senPin.init()
senPin.off()

_thread.start_new_thread(send, ())

while True:
    print(f"receiving: {recPin.value()}")
    utime.sleep_ms(100)
