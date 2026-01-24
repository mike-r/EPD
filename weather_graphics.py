# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.epd import Adafruit_EPD

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
)
icon_font = ImageFont.truetype("/home/zap/Downloads/meteocons.ttf", 48)

# Map the OpenWeatherMap icon code to the appropriate font character
# See http://www.alessioatzeni.com/meteocons/ for icons
ICON_MAP = {
    "01d": "B",
    "01n": "C",
    "02d": "H",
    "02n": "I",
    "03d": "N",
    "03n": "N",
    "04d": "Y",
    "04n": "Y",
    "09d": "Q",
    "09n": "Q",
    "10d": "R",
    "10n": "R",
    "11d": "Z",
    "11n": "Z",
    "13d": "W",
    "13n": "W",
    "50d": "J",
    "50n": "K",
}

# RGB Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Weather_Graphics:
    def __init__(self, display, *, am_pm=True, celsius=True):
        self.am_pm = am_pm
        self.celsius = celsius

        self.small_font = small_font
        self.medium_font = medium_font
        self.large_font = large_font

        self.display = display

        self._weather_icon = None
        self._city_name = None
        self._main_text = None
        self._temperature = None
        self._feels_like = None
        self._pressure = None
        self._description = None
        self._time_text = None
        self._wind_speed = None
        self._wind_deg = None

    def display_weather(self, weather):
        weather = json.loads(weather.decode("utf-8"))

        # set the icon/background
        self._weather_icon = ICON_MAP[weather["weather"][0]["icon"]]

        city_name = weather["name"] + ", " + weather["sys"]["country"]
        print(city_name)
        self._city_name = city_name.rstrip(", US")

        main = weather["weather"][0]["main"]
        print(main)
        self._main_text = main

        temperature = weather["main"]["temp"] - 273.15  # its...in kelvin
        feels_like = weather["main"]["feels_like"] - 273.15 # its also in Kelvin
        print("temperature = ", temperature, "   feels_like = ", feels_like)
        if self.celsius:
            self._temperature = "%d °C" % temperature
            self._feels_like = "%d °C" % feels_like
        else:
            self._temperature = "%d °F" % ((temperature * 9 / 5) + 32)
            self._feels_like = "%d °F" % ((feels_like * 9 / 5) + 32)

        pressure = weather["main"]["pressure"]
        if self.celsius:
            self._pressure = pressure
        else:
            self._pressure = '{0:.2f}'.format(pressure * 0.029529983071445)+" inHg"

        description = weather["weather"][0]["description"]
        description = description[0].upper() + description[1:]
        print(description)
        self._description = description

        wind_speed = weather["wind"]["speed"]
        wind_deg = weather["wind"]["deg"]
        

        if wind_speed == 0:
            self._wind_speed = "Calm"
            self._wind_deg = " "
        else:
            self._wind_speed = "%d kts" % (1.94384 * wind_speed)
            self._wind_deg = "%d °" % wind_deg
        print("wind_speed: ", self._wind_speed)
        print("wind_deg: ", self._wind_deg)

        # "thunderstorm with heavy drizzle"

        self.update_time()

    def update_time(self):
        now = datetime.now()
        self._time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
        self.update_display()

    def update_display(self):
        self.display.fill(Adafruit_EPD.WHITE)
        image = Image.new("RGB", (self.display.width, self.display.height), color=WHITE)
        draw = ImageDraw.Draw(image)
        wind_chill = "Feels: "

        # Draw the Icon
        (font_width, font_height) = icon_font.getsize(self._weather_icon)
        draw.text(
            (
                self.display.width // 2 - font_width // 2,
                self.display.height // 2 - font_height // 2 - 5,
            ),
            self._weather_icon,
            font=icon_font,
            fill=BLACK,
        )

        # Draw the city
        (font_width, font_height) = medium_font.getsize(self._city_name)
        draw.text(
            (self.display.width // 2 - font_width // 2,
            0,
            ), 
            self._city_name, 
            font=self.medium_font, 
            fill=BLACK,
        )

        # Draw the time
        (font_width, font_height_time) = medium_font.getsize(self._time_text)
        font_time_h = font_height_time * 2 - 16
        draw.text(
            (5, font_time_h),
            self._time_text,
            font=self.medium_font,
            fill=BLACK,
        )

        # Draw wind speed and direction
        (font_width, font_height) = small_font.getsize(self._wind_speed)
        draw.text(
            (5, font_time_h  + font_height + 8),
            self._wind_speed,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the Barometric Pressure
        (font_width, font_height) = small_font.getsize(self._pressure)
        draw.text(
            (
                self.display.width - font_width - 5,
                font_height_time * 2 - 12,
            ),
            self._pressure,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the main text
        (font_width, font_height_main) = large_font.getsize(self._main_text)
        draw.text(
            (5, (self.display.height - 4) - font_height_main * 2),
            self._main_text,
            font=self.large_font,
            fill=BLACK,
        )

        # Draw the description
        (font_width, font_height) = small_font.getsize(self._description)
        draw.text(
            (1, self.display.height - font_height - 8),
            self._description,
            font=self.small_font,
            fill=BLACK,
        )

        (font_width, font_height) = small_font.getsize(self._feels_like)
        draw.text(
            (
                (self.display.width - font_width -5),
                (self.display.height - 10) - (font_height * 2),
            ),
            self._feels_like,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the feels_like temperature
        (font_width_wc, font_height) = small_font.getsize(wind_chill)
        draw.text(
        (
                (self.display.width - font_width - 5 - font_width_wc),
                (self.display.height - 10) - (font_height * 2),
        ),
            wind_chill,
            font=self.small_font,
            fill=BLACK,
        )

        # Draw the temperature
        (font_width, font_height) = large_font.getsize(self._temperature)
        draw.text(
            (
                self.display.width - font_width - 5,
                (self.display.height - 4) - font_height_main * 3,
            ),
            self._temperature,
            font=self.large_font,
            fill=BLACK,
        )

        self.display.image(image)
        self.display.display()
