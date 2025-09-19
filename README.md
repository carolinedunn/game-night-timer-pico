# 🕹️ Raspberry Pi Pico Game Night Timer

A DIY **Game Night Buzzer** built with the **Raspberry Pi Pico**.  
This project is a one-button, chess-clock-style timer designed to keep board games and card games moving.  
Press the button → your turn ends → the next player’s countdown starts.  

This build uses:
- ✅ Green / Yellow / Red LEDs for status
- ✅ 16×2 I²C LCD to show active player and remaining time
- ✅ Piezo buzzer for timeout alarm
- ✅ Optional 3D-printed case
- ✅ Auto-start on boot (`main.py` on Pico)

Perfect for speeding up family game nights where players take *way too long* on their turns.  

---

## ✨ Features
- One-button control (optional two-button mode available)  
- Per-turn countdown with customizable time  
- LEDs:  
  - Green = plenty of time  
  - Yellow = running low  
  - Red = almost out / timeout  
- LCD shows **active player** + **time left**  
- Timeout alarm (descending tone + flashing red LED)  
- Auto-runs on startup from the Pico  
- 3D-printed enclosure files provided  

---

## 🛠️ Hardware
- Raspberry Pi Pico or Pico W  
- 16×2 I²C LCD (PCF8574 backpack, address `0x27` or `0x3F`)  
- 3× LEDs (green, yellow, red) + 330 Ω resistors  
- Piezo buzzer (or swap for 3.5 mm audio jack + speaker)  
- Push button(s): one required, second optional  
- Breadboard + jumper wires  
- (Optional) 3D-printed case — [Thingiverse STL files](https://www.thingiverse.com/thing:7136384)  

---

## 🔌 Wiring
| Component       | Pico Pin | Notes                       |
|-----------------|----------|-----------------------------|
| Button 1        | GP14     | main start/next button      |
| Button 2        | GP15     | optional second button      |
| Buzzer          | GP13     | PWM capable                 |
| Green LED       | GP16     | through 330 Ω resistor      |
| Yellow LED      | GP17     | through 330 Ω resistor      |
| Red LED         | GP18     | through 330 Ω resistor      |
| LCD SDA         | GP0      | I²C0 SDA                    |
| LCD SCL         | GP1      | I²C0 SCL                    |
| Power           | 3V3 / GND| common ground required      |

📷 See the [wiring diagram](pico.png) in this repo.  

---

## 💾 Setup
1. **GitClone**
   ```bash
   sudo apt update && sudo apt upgrade
   git clone https://github.com/carolinedunn/game-night-timer-pico.git
   
2. Download MicroPython UF2 file for your Pico [from this page](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3)
3. Plug in your Pico while holding down the BOOTSEL button.
4. Copy the Python files from your Pi to your Pico.
5. Open [Thonny](https://thonny.org/) and select Pico and MicroPython for the environment.
6. Wire your Pico.
7. Test your Pico.
8. Save the file you want to run on boot as main.py

---

## ▶️ Tutorial Video
🎥 YouTube tutorial: [Pico Game Night Timer](https://youtu.be/WSQV_xoQzLM)  

---

## 📂 Project Series
This is part of my **Game Night Buzzer** series:  
- [Episode 1: Raspberry Pi LED Timer](https://youtu.be/0G3-ISume2o)  
- [Episode 2: Raspberry Pi LCD Timer](https://youtu.be/WSQV_xoQzLM)  
- [Episode 3: Raspberry Pi Bluetooth Speaker Timer](https://youtu.be/rIc2U7KOW9k)  
- Episode 4+: Pico & Arduino builds  

---

## 🖨️ 3D Printing
Custom 3D-printed enclosures are available here:  
👉 [Thingiverse STL files](https://www.thingiverse.com/thing:7136384)  

Choose your Pico/Raspberry Pi model base + lid type (LEDs only, LCD + buzzer, LCD only).  

---

## 📖 License
MIT License — free to use, remix, and share.  
Attribution appreciated: link back to [Caroline Dunn’s channel](https://www.youtube.com/caroline).  

---

## 📚 Author
Created by **Caroline Dunn**  
- 🌐 [carolinedunn.org](https://carolinedunn.org)  
- 📺 [YouTube.com/Caroline](https://www.youtube.com/caroline)  
- 📘 [A Woman’s Guide to Winning in Tech](https://amzn.to/3YxHVO7)  
