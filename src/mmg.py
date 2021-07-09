"""
created by Brad Hillier - BradleyHillier@icloud.com
https://github.com/BradHillier/morning-meeting-generator

generate the morning meeting self.document for Sealegs Kayaking Adventures 
in Ladysmith, BC
"""



from dataclasses import dataclass, field
from datetime import datetime
from bs4 import BeautifulSoup
from docx import Document
from time import sleep
import requests
import dateparser
import pytz
import os.path
import json
import sys
import logging

from Tide import get_tides
from Weather import get_weather
from Booking import get_bookings
import config


logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s',
                    level=logging.INFO, filename='mmg.log', filemode='a')


class MeetingDocumentGenerator:
    def __init__(self):
        config.load()
        self.document = Document()
        self.tides: dict = get_tides()
        self.weather: list[Weather] = get_weather(10,18)
        self.bookings: list[Booking] = get_bookings(config.CONFIG['calendar ID'])

    def generate(self):
        datestring = datetime.now().strftime('%A - %B %d - %Y')
        self.document.add_heading('Daily Safety Meeting', 0)
        self.document.add_paragraph(datestring)

        self._add_attendants()
        self._add_safety_topic(self.weather, self.tides)
        
        self.document.add_heading('General Notes/Maintenance', 2)
        self.document.add_paragraph('\n' * 2)

        self._add_tides()
        self._add_weather()
        self._add_bookings()

    def write_to_file(self):
        try:
            self.document.save(config.CONFIG['output location'] + 'morning_meeting_' + 
                          datetime.now().strftime('%d-%m-%y') + '.docx')
        except FileNotFoundError:
            logging.error('invalid output location, path to directory does not exist')
            sys.exit()
        logging.info('self.document successfully created')

    def _add_attendants(self):
        self.document.add_heading('Attendants', 2)
        p = self.document.add_paragraph()
        for name in config.CONFIG['employees']:
            p.add_run(f'\u2751 {name}')

    def _add_safety_topic(self, weather=None, tides=None):
        self.document.add_heading('Safety Topic', 2)
        safety_topics = list()
        if weather and any(hour.temp >= 30 for hour in weather):
            safety_topics.append(
                '''Watch out for Heat Exhaustion. Alternate staff working in the sun, drink plenty of water''')
        woods_inaccessible = [tide for tide in tides['hourly'] if \
                             tide.is_too_low_for_woods()]
        if any(tide.is_within_operational_hours() for tide in woods_inaccessible):
            start = woods_inaccessible[0].time.strftime('%I%p')
            end = woods_inaccessible[-1].time.strftime('%I%p')
            safety_topics.append(
                f'Tides too low to access channel behind Woods Island from {start} to {end}')
        self.document.add_paragraph('\n'.join(safety_topics))

    def _add_tides(self):
        self.document.add_heading('Tides', 2)
        tides_table = self.document.add_table(rows=0, cols=3)
        for tide in self.tides['high and low']:
            row_cells = tides_table.add_row().cells
            row_cells[0].text = tide.time.strftime('%-I:%M %p')
            row_cells[1].text = f'{tide.meters} meters'
            row_cells[2].text = f'{tide.feet} feet'


    def _add_weather(self):
        self.document.add_heading('Weather', 2)
        wx_table = self.document.add_table(rows=4, cols=len(self.weather))
        for i in range(len(wx_table.columns)):
            col = wx_table.columns[i]
            col.cells[0].text = self.weather[i].date.strftime('%-I:%M %p')
            col.cells[1].text = self.weather[i].emoji
            col.cells[2].text = f'{self.weather[i].temp}\N{DEGREE SIGN} C',
            col.cells[3].text = self.weather[i].wind

    def _add_bookings(self):
        self.document.add_heading('Bookings', 2)
        bookings_table = self.document.add_table(rows=0, cols=2)
        for booking in self.bookings:
            row_cells = bookings_table.add_row().cells
            start = booking.start_at.strftime('%-I:%M %p')
            end = booking.end_at.strftime('%-I:%M %p')
            row_cells[0].text = f'{start} to {end}'
            row_cells[1].text = booking.title
