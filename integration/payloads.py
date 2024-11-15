import pytz
from .helpers import escape, legal_form, get_sum
from datetime import timedelta

astana = pytz.timezone('Asia/Almaty')


def get_publish_payload(lot):
    position = lot.positions.exclude(status='DELETED').first()
    return {
        "number": str(lot.number),
        "name": escape(lot.name),
        "description": escape(lot.name),
        "datasheet": 'https://std.webmts.kz/file/%s/download/' % lot.files.filter(type='SPEC').first().id,
        "qualifications": None,
        "draftAgreement": 'https://std.webmts.kz/file/%s/download/' % lot.files.filter(type='CONTRACT').first().id,
        "sum": str(lot.sum),

        "truType": 1,
        "procurementMethod": lot.get_type_display(),
        "status": 'Опубликован',

        "publishDate": str(lot.submission_begin.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "startDate": str(lot.bidding_begin.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "endDate": str(lot.bidding_end.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),

        "organizerBin": str(lot.client.idn),
        "organizerName": escape(lot.client.name),
        "organizerPhone": escape(lot.client.phone),
        "organizerEmail": escape(lot.client.email),

        "customerBin": str(lot.company.idn),
        "customerName": escape(lot.company.name),
        "customerPhone": escape(lot.company.phone),
        "customerEmail": escape(lot.company.email),
        
        "deliveryTime": position.delivery_days,
        "termsOfPayment": position.payment_terms,
        "deliveryKato": None,
        "deliveryAddress": escape(position.delivery_terms.replace('\r\n','')),

        "externalId": str(lot.id),
        "externalCreated": str(lot.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "extraDescription": "IT IS FAKE!!! TEST PURPOSE ONLY!!!",

        "lots": [{
            "customerBin": str(lot.company.idn),
            "organizerBin": str(lot.client.idn),
        
            "number": str(lot.number),
            "name": escape(position.name),
            "description": escape(position.name),
                    
            "truCode": None,
            "truName": escape(position.name),
            "truType": 1,
            "truDescription": escape(position.name),
            "truUnit": position.unit,

            "count": str(position.quantity),
            "price": str(position.price),
            "sum": str(position.sum),

            "procurementMethod": lot.get_type_display(),
            "status": 'Опубликован', 
        
            "deliveryKato": None,
            "deliveryAddress": escape(position.delivery_terms.replace('\r\n','')),
            "deliveryTime": position.delivery_days,

            "externalId": str(position.id),
            "externalPlanId": None,
            "externalTenderId": str(lot.id),
            "externalCreated": str(lot.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
            "extraDescription": "IT IS FAKE!!! TEST PURPOSE ONLY!!!"
        }]
    }


def get_result_payload(lot):
    position = lot.positions.exclude(status='DELETED').first()
    return {   
        "number": str(lot.number),
        "name": escape(lot.name),
        "description": escape(lot.name),

        "procurementMethod": lot.get_type_display(),
        "status": lot.get_status_display(),
        
        "deliveryConditions": escape(position.delivery_terms.replace('\r\n','')),

        "truCode": None,
        "truName": escape(position.name),
        "truType": 1,

        "currency": "KZT",
        "count": str(position.quantity),

        "openingPrice": str(lot.sum),
        "closingPrice": str(lot.result.bid.sum) if lot.result.status == 'HAS_WINNER' else None,
        "weightedAveragePrice": None,

        "price": str(position.price),
        "priceWithNds": str(get_sum(lot.vat, position.price)),

        "sum": str(lot.sum),
        "sumWithNds": str(get_sum(lot.vat, lot.sum)),

        "actualSum":        str(lot.result.bid.sum) if lot.result.status == 'HAS_WINNER' else None,
        "actualSumWithNds": str(get_sum(lot.vat, lot.result.bid.sum)) if lot.result.status == 'HAS_WINNER' else None,

        "planCount": None,
        "planPrice": None,
        "planSum": None,

        "customerBin": str(lot.client.idn),
        "customerName": escape(lot.client.name),
        "customerPhone": escape(lot.client.phone),
        "customerEmail": escape(lot.client.email),
        "customerStockId": None,

        "providerBin":   str(lot.result.bid.application.client.idn)      if lot.result.status == 'HAS_WINNER' else None,
        "providerName":  escape(lot.result.bid.application.client.name)  if lot.result.status == 'HAS_WINNER' else None,
        "providerPhone": escape(lot.result.bid.application.client.phone) if lot.result.status == 'HAS_WINNER' else None,
        "providerEmail": escape(lot.result.bid.application.client.email) if lot.result.status == 'HAS_WINNER' else None,
        "providerStockId": None,

        "createDate": str(lot.result.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "acceptDate": str(lot.result.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "endDate":    str(lot.result.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),

        "localContent": None,

        "externalId": str(lot.result.id),
        "externalPlanId": None,
        "externalTenderId": str(lot.id),
        "externalLotId": str(position.id),
        "externalCreated": str(lot.result.created_at.replace(microsecond=0).replace(tzinfo=None) + timedelta(hours=6)),
        "extraDescription": "IT IS FAKE!!! TEST PURPOSE ONLY!!!",
    }


def get_company_payload(company):
    return {
        "bin": str(company.idn),
        "name": escape(company.name),
        "type": None,
        "legal_address": escape(company.address),
        "actual_address": escape(company.address),
        "director_name": None,
        "director_iin": None,
        "phone": escape(company.phone),
        "email": escape(company.email),
        "website": None,
        "extra_description": "IT IS FAKE!!! TEST PURPOSE ONLY!!!",
    }
