# MicroPython: 16x2 I2C LCD (PCF8574) minimal driver + demo
import utime as time
from machine import I2C, Pin

class I2cLcd:
    def __init__(self, i2c, addr, cols=16, rows=2):
        self.i2c, self.addr, self.cols, self.rows = i2c, addr, cols, rows
        self.backlight = 0x08  # backlight ON
        # 4-bit init sequence
        self._write4(0x03); time.sleep_ms(5)
        self._write4(0x03); time.sleep_ms(5)
        self._write4(0x03); self._write4(0x02)    # 4-bit mode
        self.command(0x28)  # function set: 2 lines, 5x8 dots
        self.command(0x0C)  # display on, cursor off, blink off
        self.clear()
        self.command(0x06)  # entry mode: increment, no shift

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

    # Alias so existing code using write_string(...) works
    def write_string(self, s):
        self.write(s)

    def clear(self):
        self.command(0x01)
        time.sleep_ms(2)

    def set_cursor(self, col, row):
        addr = col + (0x40 * row)
        self.command(0x80 | addr)

# --- Init once ---
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # Pico I2C0 on GP1/GP0
# If unsure of address, do: print(i2c.scan())
LCD_ADDR = 0x27  # or 0x3F on some backpacks
lcd = I2cLcd(i2c, LCD_ADDR, 16, 2)

# --- Demo loop ---
while True:
    lcd.set_cursor(0, 0)
    lcd.write_string('Hello, world!')
    lcd.set_cursor(0, 1)
    lcd.write_string('It works! :)')
    time.sleep(2)
    lcd.clear()
    time.sleep(0.5)
