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
        return self.meters <= 0.6

    def is_within_operational_hours(self) -> bool:

        # TODO: make operational hours dynamic, config file?
        return 9 <= self.time.hour <= 16

    def __str__(self):
        time = self.time.strftime('%-I:%M %p')
        return f'{self.meters}m @ {time}'

    def __repr__(self):
        return str(self)


def get_tides() -> list:
    '''Retreive today's tides from 'Fisheries and Oceans Canada'.'''
    now = datetime.now()
    url = 'https://tides.gc.ca/eng/station?type=0&date={}%2F{}%2F{}&sid=7460&tz=PDT&pres=1'.format(
        now.year, '%02d'%now.month, now.day)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    tides = {}
    tides['high and low'] = parse_high_and_low_tides(soup)
    tides['hourly'] = parse_hourly_tides(soup)
    return tides

def parse_high_and_low_tides(soup: BeautifulSoup) -> list:
    time = soup.table.tbody.findAll('td', class_='time')
    meters = soup.table.tbody.findAll('td', class_='heightMeters')
    feet = soup.table.tbody.findAll('td', class_='heightFeet')
    return [Tide(dateparser.parse(
                    time[i].text), 
                    float(meters[i].text),
                    float(feet[i].text,)) \
            for i in range(len(time))]

def parse_hourly_tides(soup: BeautifulSoup) -> list:
    table = soup.find(title='Predicted Hourly Heights (m)').tbody
    raw_tides = table.tr.find_all('td')
    tides = list()
    for i in range(24):
        date = dateparser.parse('midnight today').replace(hour=i)
        meters = 0.5
        feet = '%.1f'%(meters * 3.2808)
        tides.append(Tide(date, meters, feet))
    return tides
