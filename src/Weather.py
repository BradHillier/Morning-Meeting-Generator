from dataclasses import dataclass
from datetime import datetime
import dateparser
import requests
from math import ceil


@dataclass
class Weather:
    date: datetime
    description: str
    emoji: str
    temp: int
    wind: str
    uv: int

    def __str__(self):
        attrs = [
            self.date.strftime('%-I%p'),
            self.description,
            str(self.temp) + u'\N{DEGREE SIGN}' + 'C',
            self.wind,
            str(self.uv)
        ]
        return ' - '.join(attrs)


def get_api_weather(start_time: int, end_time: int, api_key: str) -> list[Weather]:
   """
   start_time: in 24 hour format, the first hour to get weather data for
   end_time: in 24 hour format, the last hour to get weather data for

   gets weather data from start time to end time from weather api
   return a list of all weather objects created
   """

   # TODO: load town from database
   url = "http://api.weatherapi.com/v1/forecast.json"
   res = requests.get(url, params={
         "q": "ladysmith", 
         "key": api_key
      })
   hourly_wx = []

   # TODO: Add error checking for a bad response
   hours: list = res.json()['forecast']['forecastday'][0]['hour']
   for hour in hours[start_time:end_time + 1]:
      hourly_wx.append(parse_api_hour(hour))
   return hourly_wx


def parse_api_hour(hour: dict) -> Weather:
    """
    given a dict contain the raw output from the weather API,
    create a weather object and return it
    """
    date = dateparser.parse(hour['time'])
    description = hour['condition']['text']

    # icon is originally a url, [20:] remove upto the ....com/ from the url
    # the remaining is the path to the .png file in the weather directory
    emoji = hour['condition']['icon'][20:]
    temp = ceil(hour['temp_c'])
    wind = f"{hour['wind_dir']} {round(hour['wind_kph'])}"
    uv = hour['uv']
    return Weather(date, description, emoji, temp, wind, uv)
