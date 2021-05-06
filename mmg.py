from bs4 import BeautifulSoup
import requests


def fetch_tides() -> list:
    """
    return list containing tuples of the format (time: str, height: str);
    tides will be in order of earliest to latest
    """
    res = requests.get('https://tides.gc.ca/eng/station?sid=7460')
    html = res.content
    soup = BeautifulSoup(html, 'html.parser')

    time = soup.table.tbody.findAll('td', class_='time')
    height = soup.table.tbody.findAll('td', class_='heightMeters')

    return [(time[i].text, height[i].text) for i in range(len(time))]

tides = fetch_tides()
for tide in tides:
    t, h = tide
    print(f'Time: {t}, Height: {h}')



