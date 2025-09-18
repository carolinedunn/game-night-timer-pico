from machine import Pin
from utime import sleep

gled = Pin(16, Pin.OUT)
yled = Pin(17, Pin.OUT)
rled = Pin(18, Pin.OUT)

while True:
    gled.value(1)
    print("green")
    sleep(1)
    gled.value(0)
    yled.value(1)
    print("yellow")
    sleep(1)
    yled.value(0)
    rled.value(1)
    print("red")
    sleep(1)
    rled.value(0)