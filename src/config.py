"""
load configuration file for morning meeting generator
config properties will be available as a global dictionary after load() is run
"""


import json
import sys
import requests


def load():
    '''Load or create a config file'''
    try:
        with open('/Users/bradhillier/Developer/morning_meeting_generator/config.json') as f:
            global CONFIG 
            CONFIG = json.load(f)
    except FileNotFoundError:
        print('config file not found')
        generate_config_file()
    except json.JSONDecodeError:
        print('corrupted config file')
        if get_bool_from_user('Create new config file? [Y\\n]'):
            generate_config_file()
        else:
            print('Exiting program')
            sys.exit()


def get_bool_from_user(message: str, default=True) -> bool:
    user_input = None
    true = set(('y', 'yes', 't', 'true', '1'))
    false = set(('n', 'no', 'f', 'false', '0'))
    true.add('') if default else false.add('')
    while user_input not in true.union(false):
        user_input = input(message).lower()
    return True if user_input in true else False
        

def generate_config_file():
    global CONFIG 
    CONFIG = dict()
    print('\nEMPLOYEES')
    CONFIG['employees'] = [] 
    while get_bool_from_user('add employee [Y\\n]'):
        CONFIG['employees'].append(input('employee: '))

    token = get_token()
    calendars = get_calendars(token)
    while not calendars:
        token = get_token()
        calendars = get_calendars(token)

    CONFIG['personal access token'] = token

    print('\nSelect a Calendar')
    for i in range(len(calendars)):
        print(f'{i}: {calendars[i][0]}')
    while True:
        try:
            cal = int(input())
            if cal not in range(len(calendars)):
                print('invalid input')
                continue
            break
        except ValueError:
            print('invalid input')

    CONFIG['calendar ID'] = calendars[int(cal)][1]
    CONFIG['output location'] = input('path to output folder: ')
    with open('config.json', 'w') as f:
        json.dump(CONFIG, f, indent=2)


def get_calendars(token: str):
    base_url = 'https://timetreeapis.com/calendars'
    headers = {'Accept': 'application/vnd.timetree.v1+json',
               'Authorization': f'Bearer {token}'
              }
    res = requests.get(base_url, headers=headers)
    print(res.content)
    if res.ok:
        raw_calendars = res.json()['data']
        return [(cal['attributes']['name'], cal['id']) for cal in raw_calendars]
    return False


def get_token():
    token = input('personal access token: ')
    while len(token) != 48:
        print('invalid personal access token')
        token = input('personal access token: ')
    return token

