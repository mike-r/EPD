# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
This example queries the Open Weather Maps site API to find out the current
weather for your location... and display it on a eInk Bonnet!
"""

import time
import urllib.request
import urllib.parse
import digitalio
import busio
import board
from adafruit_epd.ssd1675 import Adafruit_SSD1675
from adafruit_epd.ssd1680 import Adafruit_SSD1680
from adafruit_epd.ssd1680 import Adafruit_SSD1680Z
from weather_graphics import Weather_Graphics

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)
up_button = digitalio.DigitalInOut(board.D5)
up_button.switch_to_input()
down_button = digitalio.DigitalInOut(board.D6)
down_button.switch_to_input()

# You'll need to get a token from openweathermap.org, looks like:
# 'b6907d289e10d714a6e88b30761fae22'
OPEN_WEATHER_TOKEN = "d17d032f55bfa5607ba70c65afd9a22d"
DEBOUNCE_DELAY = 0.3
city_no = 4         # Reedley Airport, CA



# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB"
LOCATION = "Albuquerque, US"

LAT = 43.07942
LON = -89.37584

DATA_SOURCE_URL = "http://api.openweathermap.org/data/2.5/weather"

if len(OPEN_WEATHER_TOKEN) == 0:
    raise RuntimeError(
        "You need to set your token first. If you don't already have one, you can register for a free account at https://home.openweathermap.org/users/sign_up"
    )

# Set up where we'll be fetching data from
params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
data_source = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(params)
print("data_source: ", data_source)

# Initialize the Display
display = Adafruit_SSD1680Z(     # New Bonnet ssd1680z [GDEY0213B74]
#display = Adafruit_SSD1680(     # Old eInk Bonnet ssd1680
#display = Adafruit_SSD1675(     # Older eInk Bonnet ssd1675
    122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy,
#    120, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy,
)

display.rotation = 1

gfx = Weather_Graphics(display, am_pm=True, celsius=False)
weather_refresh = None

while True:
    # only query the weather every 10 minutes (and on first run)
    # Check for Button Presses
    #print("up_button status: ", up_button.value)
    #print("down_button status: ", down_button.value)
    if up_button.value != down_button.value:
        if not up_button.value:
            city_no += 1
        elif not down_button.value:
            city_no -= 1
        if city_no > 5: city_no = 1
        if city_no < 1: city_no = 5

        if city_no == 1:
            weather_refresh = None
            time.sleep(DEBOUNCE_DELAY)
            # Set up where we'll be fetching data from
            LAT = 43.07942
            LON = -89.37584
            params = {"lat": LAT, "lon": LON, "appid": OPEN_WEATHER_TOKEN}
            print("lat is ", LAT, ", LON is ", LON)
            print("Location is Madison WI Capital")
            print("params: ", params)
        elif city_no == 2:
            LOCATION = "Albuquerque, US"
            print("LOCATION is ", LOCATION)
            weather_refresh = None
            time.sleep(DEBOUNCE_DELAY)
            # Set up where we'll be fetching data from
            params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
            print("params: ", params)
        elif city_no == 3:
            LOCATION = "Clovis, US"
            print("LOCATION is ", LOCATION)
            weather_refresh = None
            time.sleep(DEBOUNCE_DELAY)
            # Set up where we'll be fetching data from
            params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
            print("params: ", params)
        elif city_no == 4:
            weather_refresh = None
            time.sleep(DEBOUNCE_DELAY)
            # Set up where we'll be fetching data from
            LAT = 36.66880137330124
            LON = -119.44902966047906
            params = {"lat": LAT, "lon": LON, "appid": OPEN_WEATHER_TOKEN}
            print("lat is ", LAT, ", LON is ", LON)
            print("Location is Reedley Airport")
            print("params: ", params)
        elif city_no == 5:
            LOCATION = "Truckee, US"
            print("LOCATION is ", LOCATION)
            weather_refresh = None
            time.sleep(DEBOUNCE_DELAY)
            # Set up where we'll be fetching data from
            params = {"q": LOCATION, "appid": OPEN_WEATHER_TOKEN}
            print("params: ", params)

        data_source = DATA_SOURCE_URL + "?" + urllib.parse.urlencode(params)
        print("data_source: ", data_source)

    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        response = urllib.request.urlopen(data_source)
        if response.getcode() == 200:
            value = response.read()
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
            display_weather = 0
        else:
            print("Unable to retrieve data at {}".format(url))
        gfx.update_time()
    time.sleep(0.1)  # wait 0.1 seconds before updating anything again
