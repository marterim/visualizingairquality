from sds011 import * # Imports all functions from the SDSS011 file
sensor = SDS011("/dev/ttyUSB0")

import time
import board
import neopixel

pixel_pin = board.D18

num_pixels = 1

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)

# Turn-on PM sensor
sensor.sleep(sleep=False)
pmt_2_5, pmt_10 = sensor.query()
#rint("Startet innlesning")

pmt_2_5_value = 0.0
pmt_10_value = 0.0

def redOn():
    pixels.fill((255, 0, 0)) #red
    pixels.show()

def greenOn():
    pixels.fill((0, 255, 0)) #green
    pixels.show()

def orangeOn():
    pixels.fill((255, 165, 0)) #orange
    pixels.show()

def purpleOn():
    pixels.fill((106, 13, 173)) #purple
    pixels.show()

def turnOff():
    pixels.fill((0, 0, 0)) # off?
    pixels.show()

try:
    while pmt_10 > -1:

        pmt_2_5, pmt_10 = sensor.query()

        if pmt_2_5 != pmt_2_5_value or pmt_10 != pmt_10_value:

            if pmt_2_5 > -1 and pmt_2_5 < 10:
                print("Gront lys")
                greenOn()
                print("pm 2.5:", pmt_2_5)
                print("pm 10:", pmt_10)

                pmt_2_5_value = pmt_2_5
                pmt_10_value = pmt_10

            elif pmt_2_5 >= 10 and pmt_2_5 < 20:
                print("Gult lys")
                yellowOn()
                print("pm 2.5:", pmt_2_5)
                print("pm 10:", pmt_10)

                pmt_2_5_value = pmt_2_5
                pmt_10_value = pmt_10

            elif pmt_2_5 >= 20 and pmt_2_5 < 30:
                print("Rodt lys")
                redOn()
                print("pm 2.5:", pmt_2_5)
                print("pm 10:", pmt_10)

                pmt_2_5_value = pmt_2_5
                pmt_10_value = pmt_10
            time.sleep(1)
finally:
    turnOff()
