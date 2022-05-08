# Morning Meeting Generator

must run brew install python3-tk on macOS

This project was created to generate the morning meeting document for [Sealegs
Kayaking Adventures](https://sealegskayaking.com) in Ladysmith, BC.
Information was to be gathered daily from multiple websites and written down
onto a meeting template.  This program automates the process and saves about 10
minutes each morning.  

## How to install
    to do

## How to use
    to do
    conf file

## Technologies used


### beautifulsoup
used to scrape daily tide data from the department of [Fisheries and Oceans Canada](https://tides.gc.ca/eng/station?sid=7460)
### Selenium
browser automation tool used to scrape hourly weather data from [The Weather Network](https://theweathernetwork.com).  Selenium was used as content on The Weather Network is dynamically loaded using asyncronous javascript and no free API's fit the requirements of the program.<br><br>
<b>Relevant documentation:</b><br>
[getting started](https://selenium-python.readthedocs.io/getting-started.html)<br>
[locating elements](https://selenium-python.readthedocs.io/locating-elements.html)
### TimeTreeApp API
a call is made to timetree's API "upcoming events" endpoint to gather the
current days bookings
### Python-docx
dynamically creates a microsoft word document after gathering all the
required data from various sources


