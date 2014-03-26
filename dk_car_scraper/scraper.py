# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup


HIDDEN_TOKEN_NAME = 'dmrFormToken'
SEARCH_FORM_NAME = 'kerne_vis_koeretoej{actionForm.soegeord}'

CAPITALIZED_BRANDS = ['VW', 'BMW']


def get_car_details(license_plate, details=False):
    session = requests.Session()

    token = _get_token(session)
    if not token:
        #Bad result - skat probably down
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

    try:
        model_string = values[0][1].text
        date_string = values[1][1].text
    except IndexError:
        #Bad result - skat probably down
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

    # Nice formatting of car make - except if VW or BMW
    if car_make not in CAPITALIZED_BRANDS:
        car_make = car_make.title()
    else:
        car_make = car_make.upper()

    return True, {
        'car_make': car_make,
        'car_model': car_model.title(),
        'car_version': car_version,
        'day': day,
        'month': month,
        'year': year
    }


def _technical_car_info(session):
    """Gets info from the 'Tekniske oplysninger' tab."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FvisKoeretoej%2FselectTab&kerne_vis_koeretoejdmr_tabset_tab=1&_pageLabel=vis_koeretoej_side')
    soup = BeautifulSoup(response.content)

    motor = soup.find_all(text=re.compile('Motor osv.'))

    try:
        motor_div = motor[0].parent.parent
        motor_vals = [div.find_all('span') for div in motor_div.find_all('div', 'colValue')]

        try:
            gasoline_type = motor_vals[1][0].text
        except (IndexError, AttributeError):
            gasoline_type = None

        try:
            mileage_value = motor_vals[2][0].text
        except (IndexError, AttributeError):
            mileage_value = None

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
            maximum_passengers = int(car_body_vals[9][0].text)
        except ValueError:
            maximum_passengers = None
    except (IndexError, AttributeError):
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

    try:
        insurance_company = insurance[0][0].text.strip()
    except (IndexError, AttributeError):
        insurance_company = None

    try:
        insurance_status = insurance[0][2].text.strip()
    except (IndexError, AttributeError):
        insurance_status = None

    return {
        'insurance_company': insurance_company,
        'insurance_active': insurance_status == u'Aktiv'
    }
