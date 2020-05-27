import board
import time
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import RPi.GPIO as GPIO
from sds011 import * # Imports all functions from the SDS011 file
import time

sensor = SDS011("/dev/ttyUSB0")

lcd_columns = 16
lcd_rows = 2

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

#Pin Config
lcd_rs = digitalio.DigitalInOut(board.D7)
lcd_en = digitalio.DigitalInOut(board.D8)
lcd_d7 = digitalio.DigitalInOut(board.D18)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)

# Initialise the LCD class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,lcd_d7, lcd_columns, lcd_rows)

char = bytes([0x1f,0x1f,0x1f,0x1f,0x1f,0x1f,0x1f,0x0])
lcd.create_char(0, char)

# Turn-on sensor
sensor.sleep(sleep=False)

airlevel = 0
squarecounter = 0
text = ""
lcd.clear()

timesFilled = 0

while True:
    #lcd.message = "\nLAV          HOY"
    lcd.message = "\n              x" + str(timesFilled)

    pmt_2_5, pmt_10 = sensor.query()
    print("pm 2.5:", pmt_2_5)
    print("pm 10:", pmt_10)

    airlevel += pmt_2_5
    airlevel += pmt_10
    print(airlevel)


    if airlevel > 50:
        text += "\x00"
        lcd.message = text
        squarecounter += 1
        airlevel -= 50
        print("Rest = ", airlevel)

        if squarecounter == 16:
            timesFilled += 1
            squarecounter = 0
            airlevel = 0
            lcd.clear()
            text = ""
            lcd.message = ""

    time.sleep(1)
