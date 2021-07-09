from selenium import webdriver
from datetime import datetime
from dataclasses import dataclass
import dateparser
from time import sleep

@dataclass
class Weather:
    date: datetime
    description: str
    emoji: str
    temp: int
    wind: str

    def __str__(self):
        attrs = [
            self.date.strftime('%-I %p'),
            self.description,
            self.temp + u'\N{DEGREE SIGN}' + 'C',
            self.wind
        ]
        return ' - '.join(attrs)
# No APIs I looked at offered hourly weather data for free, and content is
# loaded dynamically on "theweathernetwork.com".  because of this it was 
# necessary to use web browser automation.
def get_weather(start_time: int, end_time: int) -> list:
    '''
    Retrieve today's hourly weather data from 'The Weather Network' 
    for the provided time window

    Arguments:
    start_time -- the hour (0-23) to begin retrieving data
    end_time -- the hour (0-23) to finish grabbing data (inclusive)
    '''
    url = 'https://www.theweathernetwork.com/ca/hourly-weather-forecast/british-columbia/ladysmith'
    browser = webdriver.Safari()
    browser.get(url)
    browser.implicitly_wait(10)
    raw_hourly_wx = browser.find_elements_by_class_name('wxColumn-hourly')
    wx_legend = browser.find_elements_by_class_name('legendColumn')
    wind_index = find_wind_index(wx_legend)

    # webelements on hidden tables were showing up with empty text in Chrome. 
    # Clicking the button to show the next table solved this issue. 
    # Issue did not exist when using the Safari driver. 
    # Six hours of weather data are displayed in each table
    hourly_wx = []
    hours_per_table = 6
    num_of_tables = int(len(raw_hourly_wx) / hours_per_table)
    for i in range(num_of_tables):
        for j in range(hours_per_table):
            curr_hour_wx = parse_weather_from_webelement(
                raw_hourly_wx[hours_per_table * i + j], 
                wind_index
            )
            if curr_hour_wx.date.hour >= start_time:
                hourly_wx.append(curr_hour_wx)
            if curr_hour_wx.date.hour == end_time:
                break
        else:
            browser.find_element_by_class_name('hourlyforecast_data_table_ls_next').click()
            # content isn't available until after CSS animation is completed
            sleep(0.5)
            continue
        break

    browser.quit()
    return hourly_wx


# Table rows are dynamically generated based on information relevant to current
# days conditions
def find_wind_index(wx_legend: webdriver.remote.webelement.WebElement) -> int:
    '''
    Helper Function for get_weather
    Determine which table row contains wind data 
    '''
    for i in range(len(wx_legend)):
        if wx_legend[i].text == 'Wind (km/h)':
            return i


def parse_weather_from_webelement(column: webdriver.remote.webelement.WebElement,
                                  wind_index: int) -> Weather:
    '''
    Helper function for get_weather
    Parses data from a WebElement and creates a Weather object
    '''
    weekday = column.find_element_by_class_name('day').text
    time = column.find_element_by_class_name('date').text

    date = next_occurence(weekday, time)
    description = column.find_element_by_xpath('.//*[@class="wx_description"]').text
    emoji = emoji_from_description(description)
    temp = int(column.find_element_by_xpath('.//*[@class="wxperiod_temp"]').text)
    wind = column.find_elements_by_class_name('stripeable')[wind_index].text

    return Weather(date, description, emoji, temp, wind)


# dateparser weeks appear to start on a Saturday; when parsing without this 
# it would output the previous occurence if the weekday was less than
# now.weekday()
def next_occurence(weekday: str, time: str) -> datetime:
    '''
    Returns the next occurence of the provided weekday and time as a 
    datetime object
    helper for parse_weather_from_webelement
    '''
    now = datetime.now()
    date = dateparser.parse(' '.join([weekday, time]))
    if date.day - now.day < 0:
        return dateparser.parse(' '.join([weekday, time]), 
                                settings={'PREFER_DATES_FROM': 'future'})
    else:
        return date
    

def emoji_from_description(description: str) -> str:
    '''Return a weather emoji depicting the provided description'''

    # sun
    if description == 'Sunny': 
        return '\u2600' 

    # sun behind small cloud
    if description == 'Mainly sunny': 
        return '\U0001F324'

    # sun behind cloud
    if description in ('A mix of sun and clouds', 'Partly cloudy'): 
        return '\u26c5' 

    # sun behind large cloud
    if description in ('Cloudy with clear breaks', 'Cloudy with sunny breaks'):
        return '\U0001F325'

    # sun behind rain cloud
    if description == 'Chance of a shower':
        return '\U0001F326'

    # cloud with rain
    if description in ('Rain', 'Cloudy with showers', 'A few showers', 'Light rain'): 
        return '\U0001F327'

    # crescent moon
    if description in ('Clear', 'Mainly clear'): 
        return '\U0001F317' # crescent moon

    # cloud
    if description in ('Cloudy',  'Mainly cloudy'): 
        return '\u2601' 

    # fog
    if description == 'Fog patches':
        return '\U0001F329'

    # red question mark
    logging.warning(f'unknown weather description "{description}"')
    return '\u2753'
