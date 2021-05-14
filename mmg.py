"""
created by Brad Hillier - BradleyHillier@icloud.com
this file was created to generate the morning meeting document for
Sealegs Kayaking Adventures in Ladysmith, BC

Tides are scraped off of canadian government website using beautiful soup
Weather data is scraped off of the Weather Network using selenium
"""


from bs4 import BeautifulSoup
from docxtpl import DocxTemplate
from selenium import webdriver
from dataclasses import dataclass
from datetime import datetime
import requests
import dateparser

from convert_date import *


@dataclass
class Weather:
    date: datetime
    description: str
    temp: str
    wind: str

    def __str__(self):
        attrs = [
            self.date.strftime('%a %-I %p'),
            self.description,
            self.temp + u'\N{DEGREE SIGN}' + 'C',
            self.wind
        ]
        return ' - '.join(attrs)

@dataclass
class Tide:
    time: datetime
    meters: int
    feet: int

    def __str__(self):
        return f'{self.meters}m @ {self.time}'


def main():
    weather = get_weather()
    for i in weather:
        print(i)

def get_tides() -> list:
    """
    return [(time, height),...]
    tides will be in order of earliest to latest
    """
    res = requests.get('https://tides.gc.ca/eng/station?sid=7460')
    soup = BeautifulSoup(res.content, 'html.parser')
    time = soup.table.tbody.findAll('td', class_='time')
    height = soup.table.tbody.findAll('td', class_='heightMeters')
    return [(time[i].text, height[i].text) for i in range(len(time))]

def get_weather() -> list:
    """
    No APIs I looked at offered hourly weather data for free, and content is
    loaded dynamically on "theweathernetwork.com".  because of this it was 
    necassary to use Selenium to scrape page contents.
    """
    url = 'https://www.theweathernetwork.com/ca/hourly-weather-forecast/british-columbia/ladysmith'
    browser = webdriver.Safari()
    browser.get(url)
    browser.implicitly_wait(2)
    wx_columns = browser.find_elements_by_class_name('wxColumn-hourly')
    return [parse_weather_from_webelement(column) for column in wx_columns]

def parse_weather_from_webelement(column: webdriver.remote.webelement.WebElement) -> Weather:
    """
    Helper function for get_weather
    """
    weekday = column.find_element_by_class_name('day').text
    time = column.find_element_by_class_name('date').text
    description = column.find_element_by_xpath('.//*[@class="wx_description"]').text
    date = next_occurence(weekday, time)
    temp = column.find_element_by_xpath('.//*[@class="wxperiod_temp"]').text
    wind = column.find_elements_by_class_name('stripeable')[2].text
    return Weather(date, description, temp, wind)

def next_occurence(weekday, time):
    """
    Return next occurence of the provided weekday and time
    """
    now = datetime.now()
    date = dateparser.parse(' '.join([weekday, time]))
    if date.day - now.day < 0:
        return dateparser.parse(' '.join([weekday, time]), 
                                settings={'PREFER_DATES_FROM': 'future'})
    else:
        return date
            

def create_document():
    template = DocxTemplate('morning_meeting_template.docx')
    tides = get_tides()
    table_contents = []
    for time, height in tides:
        table_contents.append({
            'Time': time, 
            'Height': height
        })
    weather = get_weather()



if __name__ == '__main__':
    main()
