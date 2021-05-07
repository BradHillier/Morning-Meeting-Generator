from bs4 import BeautifulSoup
from docxtpl import DocxTemplate
import requests


def main():
    create_document()


def get_tides() -> list:
    """
    return [(time, height),...]
    tides will be in order of earliest to latest
    """
    res = requests.get('https://tides.gc.ca/eng/station?sid=7460')
    soup = BeautifulSoup(res.content, 'html.parser')
    time = soup.table.tbody.findAll('td', class_='time')
    height = soup.table.tbody.findAll('td', class_='heightMeters')
    return [(time[i].text, height[i].text) for i in range(len(time))]


def get_weather() -> list:
    """
    return: [(time, temperature, conditions, chance_of_percip, wind),...]
    """
    res = requests.get('https://weather.gc.ca/forecast/hourly/bc-20_metric_e.html')
    soup = BeautifulSoup(res.content, 'html.parser')

    # Ignore First 'tr' which contains only the date 
    table = soup.table.tbody.findAll('tr')[1:]
    
    # Remove rows that are not from current date
    todays_conditions = []
    for item in table:
        if len(list(item.children)) != 1:
            todays_conditions.append(item)
        else:
            # this will exit the loop on the next row containing only a date
            break

    # Parse relevant data from rows
    hourly = []
    for i in range(len(todays_conditions)):
        rows = todays_conditions[i].findAll('td')
        hourly.append([item.text.strip().replace('\xa0', ' ') for item in rows])

    return hourly


def create_document():
    template = DocxTemplate('morning_meeting_template.docx')

    tides = get_tides()
    table_contents = []
    for time, height in tides:
        table_contents.append({
            'Time': time, 
            'Height': height
        })

    weather = get_weather()
    weather_table_contents = []
    for time, temp, cond, percip, wind in weather:
        weather_table_contents.append({
            'Time': time,
            'Temp': temp,
            'Conditions': cond,
            'Wind': wind
        })

    context = {
        'table_contents': table_contents,
        'weather_table_contents': weather_table_contents
    }
    template.render(context)
    template.save('generated_meeting.docx')


if __name__ == '__main__':
    main()
