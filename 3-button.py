#3-button.py for Pico
from machine import Pin, PWM
from utime import sleep

# --- CONFIG ---
buzzer = PWM(Pin(13))        # PWM-capable
gled = Pin(16, Pin.OUT)
yled = Pin(17, Pin.OUT)
rled = Pin(18, Pin.OUT)
btn = Pin(14, Pin.IN, Pin.PULL_UP)
buzzer.duty_u16(0)

def beep(freq=1000, ms=1, vol=0.5):
    duty=int(65535*vol)
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    sleep(ms)
    buzzer.duty_u16(0)

while True:
    pressed = (btn.value() == 0)
    yled.value (1 if pressed else 0)
    gled.value (0 if pressed else 1)
    rled.value (1 if pressed else 0)
    beep(1000, 1, 0.7 if pressed else 0)
    print("press the button")
    sleep(1)
