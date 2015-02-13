# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup, element

HIDDEN_TOKEN_NAME = 'dmrFormToken'
SEARCH_FORM_NAME = 'kerne_vis_koeretoej{actionForm.soegeord}'

CAPITALIZED_BRANDS = ['VW', 'BMW']


def _get_text_value(content, *args):
    """Returns the value inside the content"""
    try:
        value = content
        for index in list(args):
            value = value[index]

        if value != content and type(value) == element.Tag:
            return True, value.text

    except (IndexError, KeyError, AttributeError):
        return False, None
    return True, None


def get_car_details(license_plate, details=False):
    session = requests.Session()

    token = _get_token(session)
    if not token:
        # Bad result - skat probably down
        return {
            "error": 500,
            "message": "Scraper not finding expected HTML structure. (Token)"
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


def _get_token(session):
    """Gets the value of the hidden search form token."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfls=false&_nfpb=true&_pageLabel=vis_koeretoej_side')

    soup = BeautifulSoup(response.content)

    try:
        return soup.find('input', attrs={'name': 'dmrFormToken'})['value']
    except (TypeError, KeyError):
        return None


def _min_car_info(session, payload):
    """Gets minimal info about car. From 'Køretøj' tab."""
    response = session.post('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FfremsoegKoeretoej%2Fsearch&_pageLabel=vis_koeretoej_side', data=payload)
    soup = BeautifulSoup(response.content)

    if "Ingen køretøjer fundet" in response.content:
        return False, {
            "error": 404,
            "message": "Car not found"
        }

    values = [div.find_all('span', attrs={'class': 'value'})
              for div in soup.find_all('div', attrs={'class': 'bluebox'})]

    r1, model_string = _get_text_value(values, 0, 1)
    r2, date_string = _get_text_value(values, 1, 1)

    if not r1 and not r2:
        return False, {
            "error": 500,
            "message": "Scraper not finding expected HTML structure."
        }

    try:
        car_make, car_model, car_version = model_string.split(', ')[:3]
        day, month, year = date_string.split('-')
    except ValueError:
        return False, {
            "error": 500,
            "message": "Scraper not finding expected HTML structure."
        }

    # Optional values
    r1, car_type = _get_text_value(values, 0, 2)
    r2, car_owner_type = _get_text_value(values, 1, 2)
    r3, last_update = _get_text_value(values, 1, 3)

    # Mileage values
    stand = soup.find_all(text=re.compile('Stand'))
    stand_section = stand[0].parent.parent
    stand_vals = [
        div.find_all('span')
        for div in stand_section.find_all('div', 'colValue')
    ]

    r4, mileage = _get_text_value(stand_vals, 0, 0)
    if r4 and mileage:
        if "-" in mileage:
            mileage = None
        else:
            mileage = int(mileage) * 1000

    # Nice formatting of car make - except if VW or BMW
    if car_make not in CAPITALIZED_BRANDS:
        car_make = car_make.title()
    else:
        car_make = car_make.upper()

    return True, {
        'car_make': car_make,
        'car_model': car_model.title(),
        'car_version': car_version,

        'car_type': car_type,
        'car_purpose': car_owner_type,
        'car_mileage': mileage,

        'day': day,
        'month': month,
        'year': year,
        'last_update': last_update,
    }


def _technical_car_info(session):
    """Gets info from the 'Tekniske oplysninger' tab."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FvisKoeretoej%2FselectTab&kerne_vis_koeretoejdmr_tabset_tab=1&_pageLabel=vis_koeretoej_side')
    soup = BeautifulSoup(response.content)

    motor = soup.find_all(text=re.compile('Motor osv.'))

    try:
        motor_div = motor[0].parent.parent
        motor_vals = [
            div.find_all('span')
            for div in motor_div.find_all('div', 'colValue')
        ]

        r1, gasoline_type = _get_text_value(motor_vals, 1, 0)
        r2, mileage_value = _get_text_value(motor_vals, 2, 0)

        try:
            mileage = float(mileage_value.replace(',', '.'))
        except ValueError:
            mileage = None

    except (IndexError, AttributeError):
        gasoline_type = None
        mileage = None

    car_body = soup.find_all(text=re.compile('Karrosseri'))

    try:
        car_body_div = car_body[0].parent.parent
        car_body_vals = [div.find_all('span')
                         for div in car_body_div.find_all('div', 'colValue')]

        try:
            r1, maximum_passengers = _get_text_value(car_body_vals, 9, 0)
            if r1 and maximum_passengers:
                maximum_passengers = int(maximum_passengers)

        except ValueError:
            maximum_passengers = None

    except (IndexError, AttributeError):
        maximum_passengers = None

    return {
        'gasoline_type': gasoline_type,
        'mileage_per_liter': mileage,
        'max_passengers': maximum_passengers
    }


def _insurance_car_info(session):
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FvisKoeretoej%2FselectTab&kerne_vis_koeretoejdmr_tabset_tab=3&_pageLabel=vis_koeretoej_side')
    soup = BeautifulSoup(response.content)

    insurance = [div.find_all('span', attrs={'class': 'value'})
                 for div in soup.find_all('div', attrs={'class': 'bluebox'})]

    r1, insurance_company = _get_text_value(insurance, 0, 0)
    if insurance_company:
        insurance_company = insurance_company.strip()

    r2, insurance_status = _get_text_value(insurance, 0, 2)
    if insurance_status:
        insurance_status = insurance_status.strip()

    return {
        'insurance_company': insurance_company,
        'insurance_active': insurance_status == u'Aktiv'
    }
