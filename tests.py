import unittest
import json
import requests
from datetime import datetime
from pytz import timezone

import src.config as config
from src.mmg import get_bookings, create_safety_topic, Weather, Tide


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


class TestSafetyTopic(unittest.TestCase):

    def setUp(self):
        day = datetime(2021, 5, 18)
        self.weather = [
            Weather(day.replace(hour=10), 'Sunny', 20, '10NE'),
            Weather(day.replace(hour=11), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=12), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=13), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=14), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=15), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=16), 'Sunny', 20, '10N'),
            Weather(day.replace(hour=17), 'Sunny', 20, '10N')
        ]
        self.tides = {
            'high and low': {
                Tide(time=day.replace(hour=3, minute=8), meters=1, feet=3.3),
                Tide(time=day.replace(hour=8, minute=5), meters=2.4, feet=7.9),
                Tide(time=day.replace(hour=15, minute=13), meters=1, feet=3.3),
                Tide(time=day.replace(hour=22, minute=52), meters=2.4, feet=7.9)
            }
            'hourly': {}
        ]

    def _adjust_temp(self, temp: int, start_hour: int, end_hour: int):
        for weather in self.weather:
            if weather.date.hour in range(start_hour, end_hour):
                weather.temp = 30

    def _adjust_tides(self, index: int, meters: int):
        self.tides[index].meters = meters
        self.tides[index].feet = '%.1f'%(meters * 3.2808)

    def test_no_warnings(self):
        self.safety_topic = create_safety_topic(weather=self.weather)
        self.assertEqual(self.safety_topic, '')

    def test_heatstroke_warning(self):
        self._adjust_temp(temp=30, start_hour=11, end_hour=16)
        self.safety_topic = create_safety_topic(weather=self.weather)
        self.assertEqual(self.safety_topic, 
             '''Watch out for Heat Exhaustion. Alternate staff working in the sun, drink plenty of water''')

    def test_too_low_to_go_behind_woods_warning(self):
        """
        Check if tide is too low to go behind woods
        """
        self._adjust_tides(index=2, meters=0.6)
        self.safety_topic = create_safety_topic(tides=self.tides)
        self.assertEqual(self.safety_topic, 'Too low to go behind woods')

    def test_no_tide_warning_outside_of_operational_hours(self):
        """
        Check if tide is too low to go behind woods
        """
        self._adjust_tides(index=0, meters=0.2)
        self.safety_topic = create_safety_topic(tides=self.tides)
        self.assertEqual(self.safety_topic, '')

    def test_warnings_on_seperate_lines(self):
        """
        Check that warning messages are seperated by newline characters
        without a trailing newline character.
        """
        self._adjust_temp(temp=30, start_hour=11, end_hour=16)
        self._adjust_tides(index=2, meters=0.6)
        self.safety_topic = create_safety_topic(
            weather=self.weather, tides=self.tides)
        self.assertEqual(self.safety_topic, 
            '''Watch out for Heat Exhaustion. Alternate staff working in the sun, drink plenty of water\nToo low to go behind woods''')




if __name__ == '__main__':
    unittest.main()

