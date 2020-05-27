import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from sds011 import * # Imports all functions from the SDSS011 file
sensor = SDS011("/dev/ttyUSB0")

import time
import board
import neopixel
import requests
import json
import datetime


sensor_on = False
api_on = False

# Buttons
GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 11 to be an input pin and set initial value to be pulled low (off)


# LED LIGHT
pixel_pin = board.D18
num_pixels = 3
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

def redOn():
    pixels.fill((255, 0, 0)) #red
    pixels.show()

def greenOn():
    pixels.fill((0, 255, 0)) #green
    pixels.show()

def yellowOn():
    pixels.fill((255, 165, 0)) #yellow
    pixels.show()

def purpleOn():
    pixels.fill((106, 13, 173)) #purple
    pixels.show()

def turnOff():
    pixels.fill((0, 0, 0)) # off?
    pixels.show()

# BUTTON
def api_buttonpressed(channel):
    global sensor_on
    global api_on
    if api_on:
        return;
    sensor_on = False
    api_on = True
    turnOff()
    time.sleep(0.7)

    print("Showing API data: ")
    timestamp = datetime.datetime.now()
    timestamp = timestamp.replace(minute=0, second=0)
    timestamp_string = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
    timestamp_string = timestamp_string + "Z"
    #print(timestamp_string)
    measuredValues = getTimemeasurement(timestamp_string)

    #print(measuredValues)
    final_color_values = checkpollutionlevels(measuredValues)
    meanAirQuality = getmeancolor(final_color_values)
    print(meanAirQuality)
    turnOn_LED(meanAirQuality)
    time.sleep(0.5)

def sensor_buttonpressed(channel):
    global sensor_on
    global api_on
    if sensor_on:
        return;
    api_on = False
    sensor_on = True
    turnOff()
    time.sleep(0.7)

    print("Showing sensor data: ")

    # Turn-on PM sensor
    sensor.sleep(sleep=False)
    pm25, pm10 = sensor.query()



    # Cheking pollutionlevel
    pollutionlevel = sensor_pollutionlevel(pm10, pm25)
    print(pollutionlevel)
    turnOn_LED(pollutionlevel)
    time.sleep(0.5)

def turnOn_LED(color):
    if color == "green":
        greenOn()
    elif color == "yellow":
        yellowOn()
    elif color == "red":
        redOn()
    else:
        purpleOn()

def sensor_pollutionlevel(pm10_measurement, pm25_measurement):
    green = 0
    yellow = 0
    red = 0
    purple = 0

    if pm10_measurement >= 0 and pm10_measurement <= 60:
        green += 1
    elif pm10_measurement >= 60 and pm10_measurement <= 120:
        yellow += 1
    elif pm10_measurement >= 120 and pm10_measurement <= 400:
        red += 1
    elif pm10_measurement >= 400 and pm10_measurement <= 800:
        purple += 1

    if pm25_measurement >= 0 and pm25_measurement <= 30:
        green += 1
    elif pm25_measurement >= 30 and pm25_measurement <= 50:
        yellow += 1
    elif pm25_measurement >= 50 and pm25_measurement <= 150:
        red += 1
    elif pm25_measurement >= 150 and pm25_measurement <= 200:
        purple += 1

    level = ""
    level = checksensormean(green, yellow, red, purple)
    return level


def checksensormean(green, yellow, red, purple):
    if purple >= 1:
        return "purple"
    elif red >= 1:
        return "red"
    elif yellow >= 1:
        return "yellow"
    else:
        return "green"


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

# API
response = requests.get("https://api.met.no/weatherapi/airqualityforecast/0.1/?lat=59.95122299&lon=10.73399931") #lat and lon equals Nils Bays vei 82
response2 = requests.get("https://api.met.no/weatherapi/airqualityforecast/0.1/aqi_description") #description of levels

timestamp_list = response.json()["data"]["time"]
different_sources = response2.json()["variables"]

pm25_limits = []
pm25_colors = []

pm10_limits = []
pm10_colors = []

no2_limits = []
no2_colors = []

o3_limits = []
o3_colors = []


def getPollutionlevels(): #gets the different pollution levels from the API and the corresponding color
    for pollutionlevel in different_sources["pm25_concentration"]["aqis"]:
        pm25_limits.append(pollutionlevel["wms_minmax"])
        pm25_colors.append(pollutionlevel["color"])

    for pollutionlevel in different_sources["pm10_concentration"]["aqis"]:
        pm10_limits.append(pollutionlevel["wms_minmax"])
        pm10_colors.append(pollutionlevel["color"])

    for pollutionlevel in different_sources["no2_concentration"]["aqis"]:
        no2_limits.append(pollutionlevel["wms_minmax"])
        no2_colors.append(pollutionlevel["color"])

    for pollutionlevel in different_sources["o3_concentration"]["aqis"]:
        o3_limits.append(pollutionlevel["wms_minmax"])
        o3_colors.append(pollutionlevel["color"])

def getTimemeasurement(time):
    realtime = time
    for timestamp in timestamp_list: # looks for given timestamp in list of timestamps
        if timestamp["from"] == realtime:
                no2 = timestamp["variables"]["no2_concentration"]["value"]
                pm10 = timestamp["variables"]["pm10_concentration"]["value"]
                pm25 = timestamp["variables"]["pm25_concentration"]["value"]
                o3 = timestamp["variables"]["o3_concentration"]["value"]

                values = {"no2":no2, "pm10":pm10, "pm25":pm25, "o3":o3}
                return values

def checkpollutionlevels(measuredValues_list):
    rightlevelpm25_index = -1
    pm25_value = measuredValues_list["pm25"]
    pm10_value = measuredValues_list["pm10"]
    no2_value = measuredValues_list["no2"]
    o3_value = measuredValues_list["o3"]

    pm25_color = ""
    pm10_color = ""
    no2_color = ""
    o3_color = ""
    for i in range(len(pm25_limits)):
        pm25_thelimits = pm25_limits[i]
        pm25_lowerlimit = pm25_thelimits[0]
        pm25_higherlimit = pm25_thelimits[1]

        if pm25_value >= pm25_lowerlimit and pm25_value <= pm25_higherlimit:
            pm25_color = pm25_colors[i]
            break;

    for i in range(len(pm10_limits)):
        pm10_thelimits = pm10_limits[i]
        pm10_lowerlimit = pm10_thelimits[0]
        pm10_higherlimit = pm10_thelimits[1]

        if pm10_value >= pm10_lowerlimit and pm10_value <= pm10_higherlimit:
            pm10_color = pm10_colors[i]
            break;

    for i in range(len(no2_limits)):
        no2_thelimits = no2_limits[i]
        no2_lowerlimit = no2_thelimits[0]
        no2_higherlimit = no2_thelimits[1]

        if no2_value >= no2_lowerlimit and no2_value <= no2_higherlimit:
            no2_color = no2_colors[i]
            break;

    for i in range(len(o3_limits)):
        o3_thelimits = o3_limits[i]
        o3_lowerlimit = o3_thelimits[0]
        o3_higherlimit = o3_thelimits[1]

        if o3_value >= o3_lowerlimit and o3_value <= o3_higherlimit:
            o3_color = o3_colors[i]
            break;


    return {"pm25": pm25_color, "pm10":pm10_color, "no2":no2_color, "o3":o3_color}

def getmeancolor(realtimecolors):
    green = 0
    yellow = 0
    red = 0
    purple = 0

    for _,colorvalue in realtimecolors.items():
        if colorvalue == "#3F9F41":
            green += 1
        elif colorvalue == "#FFC1300":
            yellow += 1
        elif colorvalue == "#C13500":
            red += 1
        else:
            purple += 1

    if purple >= 1:
        return "purple"
    elif red >= 1:
        return "red"
    elif yellow >= 1:
        return "yellow"
    else:
        return "green"

# MAIN
getPollutionlevels() # this is constant values that are feched everytime the program starts
print("Program is running")
GPIO.add_event_detect(17, GPIO.RISING, callback=sensor_buttonpressed) # Setup event on pin 11 rising edge
GPIO.add_event_detect(15, GPIO.RISING, callback=api_buttonpressed) # Setup event on pin 10 rising edge

while True:
    if sensor_on:
        # Turn-on PM sensor
        sensor.sleep(sleep=False)
        pm25, pm10 = sensor.query()
        measured_pollutionlevel = sensor_pollutionlevel(pm10, pm25)
        print("Sensor measure in loop: ", measured_pollutionlevel)
        turnOn_LED(measured_pollutionlevel)

    elif api_on:
        timestamp = datetime.datetime.now()
        timestamp = timestamp.replace(minute=0, second=0)
        timestamp_string = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        timestamp_string = timestamp_string + "Z"
        #print(timestamp_string)
        measuredValues = getTimemeasurement(timestamp_string)

        #print(measuredValues)
        final_color_values = checkpollutionlevels(measuredValues)
        meanAirQuality = getmeancolor(final_color_values)
        print("API  measure in loop: ",meanAirQuality)
        turnOn_LED(meanAirQuality)
    time.sleep(0.5)

message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up
turnOff()
