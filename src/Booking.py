from dataclasses import dataclass, field
from datetime import datetime
import requests
import config
import dateparser
import pytz


@dataclass 
class Booking:
    title: str
    all_day: bool
    start_at: datetime
    end_at: datetime

    def __str__(self):
        start = self.start_at.strftime('%I:%M %p').strip('0')
        end = self.end_at.strftime('%I:%M %p').strip('0')
        return f'{self.title} from {start} to {end}'


def get_bookings(cal_id) -> list:
    '''
    Retrieve bookings from timetree's API upcoming_events endpoint
    Returns only current days upcoming bookings
    '''
    token = config.CONFIG['personal access token']
    base_url = 'https://timetreeapis.com/'

    res = requests.get( f'{base_url}/calendars/{cal_id}/upcoming_events',
        headers = {
            'accept': 'application/vnd.timetree.v1+json',
            'Authorization': f'Bearer {token}'
        },
        params = {
            'timezone': 'America/Vancouver'
        })

    raw_bookings = res.json()['data']
    bookings = [create_booking_obj(raw) for raw in raw_bookings]

    return [booking for booking in bookings if \
           booking.start_at.day == datetime.now().day]
        


def create_booking_obj(raw_event: dict) -> Booking:
    '''
    Helper function for get_bookings
    Converts raw booking data into Booking object
    '''

    title = raw_event['attributes']['title']
    all_day = raw_event['attributes']['all_day']

    #  Timetree's API has start and end time for all day events as 00:00:00 UTC
    start = dateparser.parse(raw_event['attributes']['start_at'])
    end = dateparser.parse(raw_event['attributes']['end_at'])
    if not all_day:
        timezone = pytz.timezone('America/Vancouver')
        start = start.astimezone(timezone)
        end = end.astimezone(timezone)

    return Booking(title, all_day, start, end)
