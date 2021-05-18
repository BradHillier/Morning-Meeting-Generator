"""
created by Brad Hillier - BradleyHillier@icloud.com
generate the morning meeting document for Sealegs Kayaking Adventures 
in Ladysmith, BC
"""


from dataclasses import dataclass, field
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from docxtpl import DocxTemplate
from docx import Document
from time import sleep
import requests
import dateparser
import pytz

emoji = {
    'Sunny': '\u2600',
    'Mainly sunny': '\U0001F324',
    'Partly cloudy': '\u26c5',
    'A mix of sun and clouds': '\U0001F324',
    'Cloudy with showers': '\U0001F325',
    'Cloudy with clear breaks': '\U0001F325',
    'Chance of a shower': '\U0001F327',
    'A few showers': '\U0001F327' 
}
    


@dataclass
class Weather:
    date: datetime
    description: str
    temp: str
    wind: str

    def __str__(self):
        attrs = [
            self.date.strftime('%-I %p'),
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
        time = self.time.strftime('%-I:%M %p')
        return f'{self.meters}m @ {time}'


@dataclass 
class Booking:
    title: str
    start_at: datetime
    end_at: datetime
    description: str = field(default=None)

    def __str__(self):
        start = self.start_at.strftime('%-I %p')
        end = self.end_at.strftime('%-I %p')
        des = self.description.replace('\n', ' ')
        return f'{self.title} from {start} to {end} - {des}'



def main():
    datestring = datetime.now().strftime('%A - %B %d - %Y')
    tides = get_tides()
    weather = get_weather(10, 23)
    bookings = get_bookings()

    document = Document()
    document.add_heading('Daily Safety Meeting', 0)
    document.add_paragraph(datestring)

    document.add_heading('Attendants', 2)
    for section in ['Safety Topic', 'General Notes/Maintenance']:
        document.add_heading(section, 2)
        document.add_paragraph('\n' * 2)

    document.add_heading('Tides', 2)
    document.add_paragraph('\n'.join(str(x) for x in tides))

    document.add_heading('Weather', 2)
    table = document.add_table(rows=4, cols=len(weather))
    for i in range(len(table.columns)):
        col = table.columns[i]
        col.cells[0].text = weather[i].date.strftime('%-I %p')
        col.cells[1].text = emoji[weather[i].description]
        col.cells[2].text = weather[i].temp + u'\N{DEGREE SIGN}' + 'C',
        col.cells[3].text = weather[i].wind

    document.add_heading('Bookings', 2)
    document.add_paragraph('\n'.join(str(x) for x in bookings))


    document.save('test.docx')



def get_tides() -> list:
    '''Retreive today's tides from 'Fisheries and Oceans Canada'.'''
    res = requests.get('https://tides.gc.ca/eng/station?sid=7460')
    soup = BeautifulSoup(res.content, 'html.parser')

    time = soup.table.tbody.findAll('td', class_='time')
    meters = soup.table.tbody.findAll('td', class_='heightMeters')
    feet = soup.table.tbody.findAll('td', class_='heightFeet')

    tides = [Tide(dateparser.parse(time[i].text), meters[i].text, feet[i].text,) \
            for i in range(len(time))]

    return [tide for tide in tides if \
            tide.time.day == datetime.now().day]
        

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
    raw_hourly_weather = browser.find_elements_by_class_name('wxColumn-hourly')
    wx_legend = browser.find_elements_by_class_name('legendColumn')
    wind_index = find_wind_index(wx_legend)

    # webelements on hidden tables were showing up with empty text in Chrome. 
    # Clicking the button to show the next table solved this issue. 
    # Issue did not exist when using the Safari driver. 
    # Six hours of weather data are displayed in each table
    hourly_weather = []
    num_of_tables = int(len(raw_hourly_weather) / 6)
    for i in range(num_of_tables):
        for j in range(6):
            curr_hour_wx = parse_weather_from_webelement(
                raw_hourly_weather[6 * i + j], 
                wind_index
            )
            if curr_hour_wx.date.hour >= start_time:
                hourly_weather.append(curr_hour_wx)
            if curr_hour_wx.date.hour == end_time:
                break
        else:
            browser.find_element_by_class_name('hourlyforecast_data_table_ls_next').click()
            sleep(0.5)
            continue
        break

    browser.quit()
    return hourly_weather


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
    temp = column.find_element_by_xpath('.//*[@class="wxperiod_temp"]').text
    wind = column.find_elements_by_class_name('stripeable')[wind_index].text

    return Weather(date, description, temp, wind)


# dateparser weeks appear to start on a Saturday; when parsing without this 
# it would output the previous occurence if the weekday was less than
# now.weekday()
def next_occurence(weekday: str, time: str) -> datetime:
    '''
    Returns the next occurence of the provided weekday and time as a 
    datetime object
    '''
    now = datetime.now()
    date = dateparser.parse(' '.join([weekday, time]))
    if date.day - now.day < 0:
        return dateparser.parse(' '.join([weekday, time]), 
                                settings={'PREFER_DATES_FROM': 'future'})
    else:
        return date


def get_bookings() -> list:
    '''
    Retrieve bookings from timetree's API upcoming_events endpoint
    Returns only current days upcoming bookings
    '''
    token = '6E-18RAX47fodf5dh3TPBpylbmXr9JmZ3mBkJ0V4bqe1It0n'
    cal_id = 'Mw4DZK3sc72B'
    base_url = 'https://timetreeapis.com/'
    headers = {'accept': 'application/vnd.timetree.v1+json',
              'Authorization': f'Bearer {token}',
             }
    res = requests.get( f'{base_url}/calendars/{cal_id}/upcoming_events',
                       headers=headers)
    raw_bookings = res.json()['data']
    bookings = [create_booking_obj(raw) for raw in raw_bookings]

    return [booking for booking in bookings if \
            booking.start_at.day == datetime.now().day]


def create_booking_obj(raw_event: dict) -> Booking:
    '''
    Helper function for get_bookings
    Converts raw booking data into Booking object
    '''
    timezone = pytz.timezone('America/Vancouver')
    attrs = [
        raw_event['attributes']['title'],
        dateparser.parse(raw_event['attributes']['start_at']).astimezone(timezone),
        dateparser.parse(raw_event['attributes']['end_at']).astimezone(timezone),
        raw_event['attributes']['description']
    ]
    return Booking(*attrs)



if __name__ == '__main__':
    main()
