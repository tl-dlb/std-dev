import json
import logging
import requests
from decimal import Decimal
from django.shortcuts import render
from django.utils import timezone
from clearing.models import Wallet, Statement
from company.models import Company
from logs.models import Log
from django.contrib.auth.models import User
URL = ''

funds_free = URL + '/funds/free'
funds_hold = URL + '/funds/hold'
funds_lock = URL + '/funds/lock'
wallets_read = URL + '/wallets/'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'dnt': '1',
    'pragma': 'no-cache',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.100 Safari/537.36',
    'Content-type': 'application/json',
    'Accept': 'application/json',
    'Authorization' : 'Token 36551760a0fd2455a43dca0ea74fc7dff3413c43'
}

import logging
logger = logging.getLogger('django')
def wallet(idn):
    url = wallets_read + idn
    response = requests.get(headers=headers, url=url, verify=False)
    return response.json()


def get_wallet(idn):
    url = wallets_read + idn
    response = requests.get(headers=headers, url=url, verify=False).json()
    wallet = Wallet.objects.get(idn=idn)
    wallet.account_number = response['account_number']
    wallet.currency_code = response['currency_code']
    wallet.deposited_amount = response['deposited_amount']
    wallet.holding_amount = response['holding_amount']
    wallet.locked_amount = response['locked_amount']
    wallet.available_amount = response['available_amount']
    wallet.save()
    return wallet


def statement(id_lot, account_number, response):
    statement = Statement.objects.filter(id_operation=response['id']).exists()
    if statement:
        statement =Statement.objects.get(id_operation=response['id'])
        statement.is_active = False
        statement.save()
    else:
        account_number = Wallet.objects.get(account_number=account_number)
        Statement.objects.create(id_app=id_lot,
                             account_number=account_number,
                             type=response['type'],
                             amount=response['amount'],
                             id_operation=response['id'],
                             is_active=response['is_active'])

def post(payload, url):
    data = json.dumps(payload, ensure_ascii=False, default=str).encode('utf-8')
    response = requests.post(headers=headers, url=url, data=data, verify=False)
    user = User.objects.get(id=1)
    Log.objects.create(comment=f'{response.url} |  {response.status_code}  |   | {response.text}',created_by=user)
    return response.json()

def hold(id,number,idn, amount):
    wallet = Wallet.objects.get(idn=idn)
    account_number = wallet.account_number
    data = {
        "platform": number,
        "account_number": account_number,
        "amount": amount
    }
    response = post(payload=data, url=funds_hold)
    statement(id, account_number, response)
    return response


def lock(id,account_number, id_oper, number):
    data = {
        "account_number": account_number,
        "id": id_oper,
        "date_time": timezone.now(),
        "platform": 'STANDARD',
        "number_lot": number
    }
    response = post(payload=data, url=funds_lock)
    statement(id, account_number, response)
    return response


def free(id, account_number, id_oper):
    data = {
        "account_number": account_number,
        "id": id_oper
    }
    response = post(payload=data, url=funds_free)
    statement(id, account_number, response)
    return response


def create_company(data):
    return post(payload=data, url=URL +'/company/create')
def create_client(data, id_broker):
    return post(payload=data, url=URL+f'/company/{id_broker}/add-client')


TWO_PLACES = Decimal(10) ** -2
def create_deal_information(lot):
    position = lot.positions.filter(status='ACTIVE').first()
    bid = lot.result.bid
    return {
            'platform': 'STD',
            'bidding_begin'      : lot.bidding_begin,
            'type'               : lot.type,
            'status'             : lot.status,
            'number'             : lot.number,
            'name'               : lot.name,
            'payment_terms'      : position.payment_terms,
            'delivery_terms'     : position.delivery_terms,
            'delivery_days'      : position.delivery_days,
            'external_code'      : position.external_code,
            'unit'               : position.unit,
            'quantity'           : position.quantity,
            'qualification'      : lot.qualification,
            'vat'                : lot.vat,
            'lot_sum'            : lot.sum,
            'deal_sum'           : bid.sum,
            'economy_sum'        : Decimal(abs(lot.sum - bid.sum)).quantize(TWO_PLACES),
            'economy_percent'    : Decimal(abs(lot.sum - bid.sum) / lot.sum * 100).quantize(TWO_PLACES),
            'guarantee_amount_sum'     : Decimal(lot.sum * lot.guarantee_amount / 100).quantize(TWO_PLACES),
            'guarantee_amount_percent' : lot.guarantee_amount,
            'positions_count'    : lot.positions.count(),
            'applications_count' : lot.applications.count(),
            'admitted_applications_count' : lot.applications.filter(status='ADMITTED').count(),
            'buyer_company_idn'      : lot.company.idn,
            'buyer_client_idn'       : lot.client.idn,
            'seller_company_idn'     : bid.application.company.idn,
            'seller_client_idn'      : bid.application.client.idn,
            'cancel_before_comment' : '',
            'cancel_after_comment'  : '',
        }


def deal(lot):
    data = create_deal_information(lot)
    return post(payload=data, url=URL +'/create_deal')
