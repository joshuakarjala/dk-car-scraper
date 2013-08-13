# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


HIDDEN_TOKEN_NAME = 'dmrFormToken'
SEARCH_FORM_NAME = 'kerne_vis_koeretoej{actionForm.soegeord}'


def get_car_details(license_plate):
    session = requests.Session()

    token = _get_token(session)

    payload = {
        HIDDEN_TOKEN_NAME: token,
        SEARCH_FORM_NAME: license_plate
    }

    return _min_car_info(session, payload)


def _get_token(session):
    """Gets the value of the hidden search form token."""
    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfls=false&_nfpb=true&_pageLabel=vis_koeretoej_side')

    soup = BeautifulSoup(response.content)
    token = soup.find('input', attrs={'name':'dmrFormToken'})['value']

    return token


def _min_car_info(session, payload):
    """Gets minimal info about car. From 'Køretøj' tab."""
    response = session.post('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FfremsoegKoeretoej%2Fsearch&_pageLabel=vis_koeretoej_side', data=payload)
    soup = BeautifulSoup(response.content)

    values = [div.find_all('span', attrs={'class': 'value'}) for div in soup.find_all('div', attrs={'class': 'bluebox'})]
    model_string = values[0][1].text
    year_string = values[1][1].text

    model_array = model_string.split(', ')

    return {
        'car_make': model_array[0].title(),
        'car_model': model_array[1],
        'car_version': model_array[2],
        'year': year_string.split('-')[-1]
    }
