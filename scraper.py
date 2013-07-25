import requests
from pyquery import PyQuery as pq

def get_car_details(license_place):
    session = requests.Session()

    response = session.get('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfls=false&_nfpb=true&_pageLabel=vis_koeretoej_side')

    d = pq(response.content)
    token = d('input[name=dmrFormToken]').val()

    payload = {
        'dmrFormToken': token,
        'kerne_vis_koeretoej{actionForm.soegeord}': license_place
    }

    response = session.post('https://motorregister.skat.dk/dmr-front/appmanager/skat/dmr?_nfpb=true&_windowLabel=kerne_vis_koeretoej&kerne_vis_koeretoej_actionOverride=%2Fdk%2Fskat%2Fdmr%2Ffront%2Fportlets%2Fkoeretoej%2Fnested%2FfremsoegKoeretoej%2Fsearch&_pageLabel=vis_koeretoej_side', data=payload)
    d = pq(response.content)

    model_string = d('div.bluebox .value').eq(1).text()
    year_string = d('div.bluebox .value').eq(5).text()
    model_array = model_string.split(', ')

    return {
        'car_make': model_array[0].title(),
        'car_model': model_array[1],
        'car_version': model_array[2],
        'year': year_string.split('-')[-1]
    }