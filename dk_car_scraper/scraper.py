# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup


HIDDEN_TOKEN_NAME = 'dmrFormToken'
SEARCH_FORM_NAME = 'kerne_vis_koeretoej{actionForm.soegeord}'

CAPITALIZED_BRANDS = ['VW', 'BMW']


def get_car_details(license_plate, details=False):
    session = requests.Session()

    try:
        token = _get_token(session)
    except TypeError:
        #Bad result - skat probably down
        return {
            "error": 500
        }

    payload = {
        HIDDEN_TOKEN_NAME: token,
        SEARCH_FORM_NAME: license_plate
    }

    car_found, car_info = _min_car_info(session, payload)

    if car_found and details:
        car_info.update(_technical_car_info(session))
        car_info.update(_insurance_car_info(session))
        return car_info

    return car_info


def _get_token(session):
    """Gets the value of the hidden search form token."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfls=false&_nfpb=true&_pageLabel=vis_koeretoej_side')

    soup = BeautifulSoup(response.content)
    token = soup.find('input', attrs={'name': 'dmrFormToken'})['value']

    return token


def _min_car_info(session, payload):
    """Gets minimal info about car. From 'Køretøj' tab."""
    response = session.post('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FfremsoegKoeretoej%2Fsearch&_pageLabel=vis_koeretoej_side', data=payload)
    soup = BeautifulSoup(response.content)

    if "Ingen køretøjer fundet" in response.content:
        return False, {
            "error": 404
        }

    values = [div.find_all('span', attrs={'class': 'value'})
              for div in soup.find_all('div', attrs={'class': 'bluebox'})]

    try:
        model_string = values[0][1].text
        year_string = values[1][1].text
    except IndexError:
        #Bad result - skat probably down
        return False, {
            "error": 500
        }

    model_array = model_string.split(', ')

    # Nice formatting of car make - except if VW or BMW
    car_make = model_array[0].title()

    if car_make in CAPITALIZED_BRANDS:
        car_make = car_make.upper()

    return True, {
        'car_make': car_make,
        'car_model': model_array[1].title(),
        'car_version': model_array[2],
        'year': year_string.split('-')[-1]
    }


def _technical_car_info(session):
    """Gets info from the 'Tekniske oplysninger' tab."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FvisKoeretoej%2FselectTab&kerne_vis_koeretoejdmr_tabset_tab=1&_pageLabel=vis_koeretoej_side')
    soup = BeautifulSoup(response.content)

    motor = soup.find_all(text=re.compile('Motor osv.'))
    motor_div = motor[0].parent.parent
    motor_vals = [div.find_all('span')
                  for div in motor_div.find_all('div', 'colValue')]

    gasoline_type = motor_vals[1][0].text
    mileage_value = motor_vals[2][0].text

    try:
        mileage = float(mileage_value.replace(',', '.'))
    except ValueError:
        mileage = None

    car_body = soup.find_all(text=re.compile('Karrosseri'))
    car_body_div = car_body[0].parent.parent
    car_body_vals = [div.find_all('span')
                     for div in car_body_div.find_all('div', 'colValue')]

    try:
        maximum_passengers = int(car_body_vals[9][0].text)
    except ValueError:
        maximum_passengers = None

    return {
        'gasoline_type': gasoline_type,
        'mileage': mileage,
        'max_passengers': maximum_passengers
    }


def _insurance_car_info(session):
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FvisKoeretoej%2FselectTab&kerne_vis_koeretoejdmr_tabset_tab=3&_pageLabel=vis_koeretoej_side')
    soup = BeautifulSoup(response.content)

    insurance = [div.find_all('span', attrs={'class': 'value'})
                 for div in soup.find_all('div', attrs={'class': 'bluebox'})]

    insurance_company = insurance[0][0].text.strip()
    insurance_status = insurance[0][2].text.strip()

    return {
        'insurance_company': insurance_company,
        'insurance_active': insurance_status == u'Aktiv'
    }
