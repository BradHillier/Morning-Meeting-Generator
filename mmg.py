from bs4 import BeautifulSoup
import requests

TIDES_URL = 'https://tides.gc.ca/eng/station?sid=7460'


req = requests.get(TIDES_URL)
html = req.content
soup = BeautifulSoup(html, 'html.parser')

tide_time = soup.table.tbody.findAll('td', class_='time')
tide_height = soup.table.tbody.findAll('td', class_='heightMeters')
tides = [(tide_time[i].text, tide_height[i].text) for i in range(len(tide_time))]
print(tides)
