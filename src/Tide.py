from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import dateparser



@dataclass
class Tide:
    time: datetime
    meters: float
    feet: float

    def is_too_low_for_woods(self) -> bool:
         
        # self.meters will always be None for the first tide of the day
        # hence the need to check that it exists
        return self.meters and self.meters <= 0.6

    def is_within_operational_hours(self) -> bool:

        # TODO: make operational hours dynamic, config file?
        return 9 <= self.time.hour <= 16

    def __str__(self):
        time = self.time.strftime('%I:%M %p').strip('0')
        return f'{self.meters}m @ {time}'

    def __repr__(self):
        return str(self)


def get_tides() -> list:
    '''Retreive today's tides from 'Fisheries and Oceans Canada'.'''
    url = 'https://tides.gc.ca/en/stations/7460'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    tides = {}
    tides['high and low'] = parse_high_and_low_tides(soup)
    tides['hourly'] = parse_hourly_tides(soup)
    return tides

def parse_high_and_low_tides(soup: BeautifulSoup) -> list:
    tide_table_id = datetime.now().strftime('day-table-%Y-%m-%d')
    todays_table = soup.find(id=tide_table_id) 
    table_rows = todays_table.tbody.find_all('tr')

    time = [row.find_all('td')[0] for row in table_rows]
    meters = [row.find_all('td')[1] for row in table_rows]
    feet = [row.find_all('td')[2] for row in table_rows]
    return [Tide(dateparser.parse(
                    time[i].text), 
                    float(meters[i].text),
                    float(feet[i].text,)) \
            for i in range(len(time))]

def parse_hourly_tides(soup: BeautifulSoup) -> list:
    table = soup.find(id="readings-list-hourly-heights").tbody

    # exclude the first td, which contains the date
    raw_tides = table.find('tr').find_all('td')[1:]
    tides = list()
    for i in range(24):
        date = dateparser.parse('midnight today').replace(hour=i)

        # Handle a blank td in table row
        if raw_tides[i].text == '':
           meters = None
           feet = None
        else:
           meters = float(raw_tides[i].text)
           feet = '%.1f'%(meters * 3.2808)

        tides.append(Tide(date, meters, feet))
    return tides
