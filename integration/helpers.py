from decimal import Decimal

def escape(str):
    return str.replace('"', '\"')


def legal_form(company):
    clearing_id = company.legal_form.clearing_id
    if clearing_id == 3:
        return 1000
    elif clearing_id == 6:
        return 1010
    elif clearing_id == 4:
        return 1020
    # elif clearing_id == ?:
    #     return 2000
    elif clearing_id == 7:
        return 2010
    elif clearing_id == 8:
        return 2020
    elif clearing_id == 1:
        return 2030
    elif clearing_id == 9:
        return 2040 
    elif clearing_id == 2:
        return 3000
    elif clearing_id == 10:
        return 4000
    elif clearing_id == 13:
        return 5000
    elif clearing_id == 22:
        return 4000
    elif clearing_id == 14:
        return 9060
    elif clearing_id == 15:
        return 9070
    elif clearing_id == 16:
        return 9080
    elif clearing_id == 17:
        return 9090
    # elif clearing_id == ?:
    #     return 9100
    return 9000
    

def get_sum(is_vat, sum):
    if is_vat:
        return sum
    return round(sum * Decimal(1.12),2)