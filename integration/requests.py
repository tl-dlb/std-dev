import requests
import json
from . import payloads


AUTH_TOKEN = 'x8fhgSRYTSgnbDCFYU4%73erthdxsFGW$#5^27653rwthywsdy5r'
EOZ_URL = 'https://192.168.200.67:18443/api/v1/no2_std'

PUBLISH_URL = EOZ_URL + '/announcement_with_lots/create'
RESULT_URL  = EOZ_URL + '/contract/create'
COMPANY_URL = EOZ_URL + '/organization/create'


def post(url, payload):
    return requests.post(url, 
        headers={'Content-Type':'application/json', 'Authorization':'Bearer %s' % AUTH_TOKEN}, 
        data=json.dumps(payload),
        verify=False)
    
def lot_publish(lot):
    return post(url=PUBLISH_URL, payload=payloads.get_publish_payload(lot))

def lot_result(lot):
    return post(url=RESULT_URL,  payload=payloads.get_result_payload(lot))

def company_create(company):
    return post(url=COMPANY_URL, payload=payloads.get_company_payload(company))