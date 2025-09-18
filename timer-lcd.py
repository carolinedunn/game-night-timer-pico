# Raspberry Pi Pico Two-Player Turn Timer + 16x2 I2C LCD
# LEDs + buzzer, one-button (or optional 2-button) control.
# MicroPython on Pico / Pico W

from machine import Pin, PWM, I2C
import utime

# ---------- CONFIG ----------
TURN_SECONDS = 10           # per-turn time
WARN_YELLOW = 4
WARN_RED = 2
USE_TWO_BUTTONS = False     # set True if wiring a second button on GP15

PIN_BTN1 = 14               # main button (start/switch)
PIN_BTN2 = 15               # optional: force Player 2
PIN_BUZZ = 13               # PWM-capable
PIN_G = 16; PIN_Y = 17; PIN_R = 18

# I2C (Pico I2C0 default: SDA=GP0, SCL=GP1)
I2C_SDA = 0
I2C_SCL = 1
LCD_ADDR = 0x27             # change to 0x3F if your backpack uses that

# ---------- tiny helpers ----------
def _pad16(s):
    s = "" if s is None else str(s)
    return (s + " " * 16)[:16]  # pad/truncate to 16 chars

def now_ms():
    return utime.ticks_ms()

# ---------- Minimal I2C LCD driver (HD44780 via PCF8574) ----------
class I2cLcd:
    def __init__(self, i2c, addr, cols=16, rows=2):
        self.i2c, self.addr, self.cols, self.rows = i2c, addr, cols, rows
        self.backlight = 0x08  # backlight on
        # 4-bit init
        self._write4(0x03); utime.sleep_ms(5)
        self._write4(0x03); utime.sleep_ms(5)
        self._write4(0x03); self._write4(0x02)    # 4-bit
        self.command(0x28)  # function set: 2 lines, 5x8
        self.command(0x0C)  # display on, cursor off
        self.clear()
        self.command(0x06)  # entry mode: inc, no shift

    def _write4(self, data, rs=0):
        # PCF8574: D7..D4 on P7..P4, EN=0x04, RS=0x01
        b = (data << 4) | self.backlight | (0x01 if rs else 0x00)
        self.i2c.writeto(self.addr, bytes([b | 0x04]))   # EN high
        self.i2c.writeto(self.addr, bytes([b & ~0x04]))  # EN low

    def command(self, cmd):
        self._write4(cmd >> 4, 0)
        self._write4(cmd & 0x0F, 0)

    def write_char(self, ch):
        c = ord(ch)
        self._write4(c >> 4, 1)
        self._write4(c & 0x0F, 1)

    def write(self, s):
        for ch in s:
            self.write_char(ch)

    def write_string(self, s):  # alias
        self.write(s)

    def clear(self):
        self.command(0x01)
        utime.sleep_ms(2)

    def set_cursor(self, col, row):
        addr = col + (0x40 * row)
        self.command(0x80 | addr)

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

# LCD init
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400000)
lcd = I2cLcd(i2c, LCD_ADDR, 16, 2)

def lcd_idle(top="Press to start", bot="  Game Night Timer"):
    lcd.clear()
    lcd.set_cursor(0, 0); lcd.write_string(_pad16(top))
    lcd.set_cursor(0, 1); lcd.write_string(_pad16(bot))

def lcd_show(player, remaining):
    lcd.set_cursor(0, 0); lcd.write_string(_pad16("Player %d" % player))
    lcd.set_cursor(0, 1); lcd.write_string(_pad16("Time: %3ds" % remaining))

def lcd_timeout():
    lcd.clear()
    lcd.set_cursor(0, 0); lcd.write_string(_pad16("  TIME IS UP"))
    lcd.set_cursor(0, 1); lcd.write_string(_pad16("Press for next"))

# ---------- State ----------
# IDLE -> P1_RUNNING / P2_RUNNING -> TIMEOUT
state = "IDLE"
active_player = 1
deadline_ms = 0
last_shown_sec = None

# ---------- Utils ----------
def now(): return utime.ticks_ms()

def beep(freq=1000, ms=120, vol=0.5):
    duty = int(65535 * max(0.0, min(1.0, vol)))
    buzz.freq(freq)
    buzz.duty_u16(duty)
    utime.sleep_ms(ms)
    buzz.duty_u16(0)

def start_turn(player):
    global state, active_player, deadline_ms, last_shown_sec
    active_player = player
    deadline_ms = utime.ticks_add(now(), TURN_SECONDS * 1000)
    state = "P1_RUNNING" if player == 1 else "P2_RUNNING"
    last_shown_sec = None  # force immediate LCD update

    # start tones: 2 beeps for P1, 3 for P2
    count = 2 if player == 1 else 3
    f = 1200 if player == 1 else 900
    for _ in range(count):
        beep(f, 80, 0.5)
        utime.sleep_ms(70)

    # initial LCD
    lcd_show(active_player, TURN_SECONDS)

def next_player():
    start_turn(2 if active_player == 1 else 1)

def read_button(pin_obj):
    if pin_obj is None:
        return False
    if pin_obj.value() == 0:
        utime.sleep_ms(35)  # debounce
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
        set_leds(False, False, True); utime.sleep_ms(120)
        set_leds(False, False, False); utime.sleep_ms(120)

# ---------- Main loop ----------
print("Pico Game Timer + LCD ready. Press BTN1 to start Player 1.")
set_leds(False, False, False)
lcd_idle()

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
            start_turn(2)
            while btn2.value() == 0:
                utime.sleep_ms(10)

        # Run countdown state
        if state in ("P1_RUNNING", "P2_RUNNING"):
            remaining_ms = utime.ticks_diff(deadline_ms, now())
            remaining_s = remaining_ms // 1000 if remaining_ms > 0 else 0

            # LEDs
            update_lights(remaining_s)

            # LCD (update only when the second changes to reduce I2C traffic)
            if remaining_s != last_shown_sec:
                lcd_show(active_player, remaining_s)
                last_shown_sec = remaining_s

            if remaining_ms <= 0:
                state = "TIMEOUT"
                set_leds(False, False, False)
                timeout_alarm()
                lcd_timeout()  # show timeout UI

        else:
            # Idle / Timeout: small sleep to reduce CPU
            utime.sleep_ms(20)

except KeyboardInterrupt:
    pass
finally:
    set_leds(False, False, False)
    buzz.duty_u16(0)
    lcd.clear()
