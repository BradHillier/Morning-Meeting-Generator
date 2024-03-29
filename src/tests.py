import unittest
import json
import requests
from datetime import datetime
from pytz import timezone

import config as config
from Booking import get_bookings
from SafetyTopics import split_hours
from Weather import *
import Tide


class TestGetBookings(unittest.TestCase):

    def setUp(self):
        config.load()
        self.token = config.CONFIG['personal access token']
        self.base_url = 'https://timetreeapis.com/' 
        self.cal_id = 'hDxoVNUBhrPi'
        self.headers = {'accept': 'application/vnd.timetree.v1_json',
                       'Authorization': f'Bearer {self.token}'}

        self.now = datetime.now(timezone('America/Vancouver')) \
            .replace(microsecond=0)

        self.midnight = datetime.now() \
            .replace(hour=0, minute=0, second=0, microsecond=0)
        self.midnight = self.midnight.replace(tzinfo=timezone('UTC'))
        utc = timezone('UTC')

        data = list()
        self.booking_id = list()

        data.append({
            'data': {
                'attributes': {
                    'title': 'test booking 0',
                    'category': 'schedule',
                    'all_day': True,
                    'start_at': self.midnight.isoformat(),
                    'end_at': self.midnight.isoformat()
                },
                'relationships': {
                    'label': {
                        'data': {
                            'id': '1',
                            'type': 'label'
                        }
                    }
                }
            }
        })
        data.append({
            'data': {
                'attributes': {
                    'title': 'test booking 1',
                    'category': 'schedule',
                    'all_day': False,
                    'start_at': self.now.astimezone(utc).isoformat(),
                    'end_at': self.now.astimezone(utc).isoformat()
                },
                'relationships': {
                    'label': {
                        'data': {
                            'id': '1',
                            'type': 'label'
                        }
                    }
                }
            }
        })
        for raw_booking in data:
            res = requests.post(
                f'{self.base_url}/calendars/{self.cal_id}/events',
                headers=self.headers, json=raw_booking)
            self.booking_id.append(json.loads(res.text)['data']['id'])
    
    def tearDown(self):
        for id in self.booking_id:
            requests.delete(
                f'{self.base_url}/calendars/{self.cal_id}/events/{id}',
                headers=self.headers)

    def test_get_full_day_booking(self):
        booking = get_bookings(self.cal_id)[0]
        self.assertEqual(booking.title, 'test booking 0')
        self.assertEqual(booking.all_day, True)
        self.assertEqual(booking.start_at.isoformat(), self.midnight.isoformat())
        self.assertEqual(booking.end_at.isoformat(), self.midnight.isoformat())

    
    def test_get_partial_day_booking(self):
        booking = get_bookings(self.cal_id)[1]
        self.assertEqual(booking.title, 'test booking 1')
        self.assertEqual(booking.all_day, False)
        self.assertEqual(booking.start_at.isoformat(), self.now.isoformat())
        self.assertEqual(booking.end_at.isoformat(), self.now.isoformat())


class TestSplitHours(unittest.TestCase):

    def setUp(self):
        day = datetime(2021, 5, 18)
        self.wx1 = [
            Weather(day.replace(hour=10), 'Sunny', 'emoji',  20, '10NE', 1),
            Weather(day.replace(hour=11), 'Sunny', 'emoji',  20, '10N', 1),
            Weather(day.replace(hour=12), 'Sunny', 'emoji',  20, '10N', 1),
        ]

        self.wx2 = [
            Weather(day.replace(hour=14), 'Sunny', 'emoji',  20, '10N', 1),
            Weather(day.replace(hour=15), 'Sunny', 'emoji',  20, '10N', 1),
        ]

        self.wx3 = [
            Weather(day.replace(hour=17), 'Sunny', 'emoji',  20, '10N', 1)
        ]
        self.weather = self.wx1 + self.wx2 + self.wx3;
  
    def test_split_hours(self):
        self.assertEqual(split_hours(self.weather), [self.wx1, self.wx2, self.wx3])



if __name__ == '__main__':
    unittest.main()

