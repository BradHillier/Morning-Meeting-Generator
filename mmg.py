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
import requests
import dateparser
import pytz

emoji = {
    'Sunny': '☀️',
    'Mainly sunny': '🌤',
    'Partly cloudy': '\u26c5',
    'A mix of sun and clouds': '⛅️'
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
    weather = get_weather(10, 17)
    bookings = get_bookings()

    document = Document()
    document.add_heading('Daily Safety Meeting', 0)
    document.add_paragraph(datestring)

    document.add_heading('Attendants', 2)

    document.add_heading('Safety Topic', 2)
    document.add_paragraph('\n' * 2)

    document.add_heading('General Notes/Maintenance', 2)
    document.add_paragraph('\n' * 2)

    document.add_heading('Tides', 2)
    document.add_paragraph('\n'.join(str(x) for x in tides))

    document.add_heading('Weather', 2)
    table = document.add_table(rows=4, cols=len(weather))
    for i in range(len(table.columns)):
        col = table.columns[i]
        col.cells[0].text = weather[i].date.strftime('%-I %p')
        col.cells[1].text = emoji[weather[i].description]
        col.cells[2].text = weather[i].temp
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
    browser.implicitly_wait(1)
    raw_hourly_weather = browser.find_elements_by_class_name('wxColumn-hourly')
    hourly_weather = [parse_weather_from_webelement(element) \
                      for element in raw_hourly_weather]
    browser.quit()

    return [weather for weather in hourly_weather if
            start_time <= weather.date.hour <= end_time and \
            weather.date.day == datetime.now().day]


def parse_weather_from_webelement(column: webdriver.remote.webelement.WebElement) -> Weather:
    '''
    Helper function for get_weather
    Parses data from a WebElement and creates a Weather object
    '''
    weekday = column.find_element_by_class_name('day').text
    time = column.find_element_by_class_name('date').text

    date = next_occurence(weekday, time)
    description = column.find_element_by_xpath('.//*[@class="wx_description"]').text
    temp = column.find_element_by_xpath('.//*[@class="wxperiod_temp"]').text
    wind = column.find_elements_by_class_name('stripeable')[2].text

    return Weather(date, description, temp, wind)


# dateparser weeks appear to start on a saturday; when parsing without this 
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
    token = 'je4zug19qFWnsNx2zS0mKKzz6caBmCQE-aggHrlV0W5XPB4K'
    cal_id = 'D5NwMz2JNMeV'
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
