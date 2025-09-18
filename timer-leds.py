# Raspberry Pi Pico Two-Player Turn Timer
# LEDs + buzzer, one-button (or optional 2-button) control.
# Works on Pico and Pico W with MicroPython.

from machine import Pin, PWM
import utime

# ---------- CONFIG ----------
TURN_SECONDS = 10           # per-turn time
WARN_YELLOW = 4
WARN_RED = 2
USE_TWO_BUTTONS = False     # set True if wiring a second button on GP15

PIN_BTN1 = 14               # main button (start/switch)
PIN_BTN2 = 15               # optional: start/switch to Player 2
PIN_BUZZ = 13               # PWM-capable
PIN_G = 16; PIN_Y = 17; PIN_R = 18

# ---------- Hardware ----------
btn1 = Pin(PIN_BTN1, Pin.IN, Pin.PULL_UP)
btn2 = Pin(PIN_BTN2, Pin.IN, Pin.PULL_UP) if USE_TWO_BUTTONS else None
buzz = PWM(Pin(PIN_BUZZ))
buzz.duty_u16(0)

led_g = Pin(PIN_G, Pin.OUT); led_y = Pin(PIN_Y, Pin.OUT); led_r = Pin(PIN_R, Pin.OUT)

def set_leds(g=False, y=False, r=False):
    led_g.value(1 if g else 0)
    led_y.value(1 if y else 0)
    led_r.value(1 if r else 0)

# ---------- State ----------
# IDLE -> P1_RUNNING / P2_RUNNING -> TIMEOUT
state = "IDLE"
active_player = 1
deadline_ms = 0

# ---------- Utils ----------
def now(): return utime.ticks_ms()

def beep(freq=1000, ms=120, vol=1):
    # vol 0..1 mapped to duty; passive piezo sounds best with modest duty
    duty = int(65535 * vol)
    buzz.freq(freq)
    buzz.duty_u16(duty)
    utime.sleep_ms(ms)
    buzz.duty_u16(0)

def start_turn(player):
    global state, active_player, deadline_ms
    active_player = player
    deadline_ms = utime.ticks_add(now(), TURN_SECONDS * 1000)
    state = "P1_RUNNING" if player == 1 else "P2_RUNNING"
    # start sound: 2 beeps for P1, 3 for P2
    count = 2 if player == 1 else 3
    f = 1200 if player == 1 else 900
    for _ in range(count):
        beep(f, 80, 0.5)
        utime.sleep_ms(70)

def next_player():
    start_turn(2 if active_player == 1 else 1)

def read_button(pin_obj):
    # simple debounce
    if pin_obj is None: 
        return False
    if pin_obj.value() == 0:
        utime.sleep_ms(40)
        return pin_obj.value() == 0
    return False

def update_lights(remaining_s):
    if remaining_s > WARN_YELLOW:
        set_leds(g=True, y=False, r=False)
    elif remaining_s > WARN_RED:
        set_leds(g=False, y=True, r=False)
    else:
        set_leds(g=False, y=False, r=True)

def timeout_alarm():
    # descending tones + red flash
    for f in (1200, 1000, 800, 600, 400):
        beep(f, 120, 1)
        utime.sleep_ms(40)
    for _ in range(6):
        set_leds(False, False, True)
        utime.sleep_ms(120)
        set_leds(False, False, False)
        utime.sleep_ms(120)

# ---------- Main loop ----------
print("Pico Game Timer ready. Press BTN1 to start Player 1.")
set_leds(False, False, False)

try:
    while True:
        # Handle button(s)
        if read_button(btn1):
            if state in ("IDLE", "TIMEOUT"):
                start_turn(1 if state == "IDLE" else (2 if active_player == 1 else 1))
            else:
                next_player()

            # wait for release
            while btn1.value() == 0:
                utime.sleep_ms(10)

        if USE_TWO_BUTTONS and read_button(btn2):
            # pressing BTN2 always starts/forces Player 2
            start_turn(2)
            while btn2.value() == 0:
                utime.sleep_ms(10)

        # Run countdown state
        if state in ("P1_RUNNING", "P2_RUNNING"):
            remaining_ms = utime.ticks_diff(deadline_ms, now())
            remaining_s = remaining_ms // 1000 if remaining_ms > 0 else 0
            update_lights(remaining_s)

            if remaining_ms <= 0:
                state = "TIMEOUT"
                set_leds(False, False, False)
                timeout_alarm()
                # wait here until next button press handled at top
        utime.sleep_ms(20)

except KeyboardInterrupt:
    pass
finally:
    set_leds(False, False, False)
    buzz.duty_u16(0)
