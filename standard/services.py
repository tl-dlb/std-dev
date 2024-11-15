from decimal import Decimal
from datetime import timedelta
from django.db.models import Sum
from .models import Lot, Position, Result

from io import BytesIO
import qrcode
import base64
import xml.etree.ElementTree as ET


def calc_lot_sum(lot) -> Lot:
    calc_sum = lot.positions.filter(status='ACTIVE').aggregate(total=Sum('sum'))
    lot.sum = calc_sum['total'] if calc_sum['total'] else 0
    lot.full_clean()
    lot.save()
    return lot

def calc_position_sum(position) -> Position:
    position.price = Decimal(position.sum / position.quantity).quantize(Decimal(10) ** -2)
    position.full_clean()
    position.save()
    return position

def set_bidding_end(lot):
    lot.bidding_end = lot.bidding_begin + timedelta(minutes=15)
    lot.full_clean()
    lot.save()
    return lot

def update_bidding_end(lot):
    lot.bidding_end = lot.bidding_end + timedelta(minutes=5)
    lot.full_clean()
    lot.save()
    return lot

def create_result(lot, status, user):
    result = Result.objects.create(
        lot=lot,
        status=status,
        created_by=user,
        updated_by=user,
    )
    result.full_clean()
    result.save()
    return result

def get_qr_codes(signature):

    '''
    data = signature.data
    size = 128
    chunks = [data[i:i+size] for i in range(0, len(data), size)]
    '''
    if signature:
        doc = ET.fromstring(signature.data)
        namespaces = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
        dsSignature = doc.find('ds:Signature', namespaces)
        dsSignatureValue = dsSignature.find('ds:SignatureValue', namespaces)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(dsSignatureValue.text)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return img_str
    return None

def get_exchange(exchange):
    for item in exchange.findall("./item[title='CNY']"):
        cny = item.find('description').text
    for item in exchange.findall("./item[title='EUR']"):
        eur = item.find('description').text
    for item in exchange.findall("./item[title='USD']"):
        usd = item.find('description').text
    for item in exchange.findall("./item[title='RUB']"):
        rub = item.find('description').text
    return cny, eur, usd, rub