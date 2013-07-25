import requests
from bs4 import BeautifulSoup

def get_car_details(license_place):
    session = requests.Session()

    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfls=false&_nfpb=true&_pageLabel=vis_koeretoej_side')

    soup = BeautifulSoup(response.content)
    token = soup.find('input', attrs={'name':'dmrFormToken'})['value']

    payload = {
        'dmrFormToken': token,
        'kerne_vis_koeretoej{actionForm.soegeord}': license_place
    }

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