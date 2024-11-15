import openpyxl
import io
import zipfile
import requests
from decimal import Decimal
from datetime import datetime
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
import xml.etree.ElementTree as ET
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from authentication.helpers import get_profile_or_403
from authentication.models import UserLoginHistory
from standard.models import Application, Result, Lot
from standard import services
from .tables import UserTable, AppTable, ResultTable, AppFilter, ResultFilter, UserFilter
from xhtml2pdf import pisa

@login_required
def log_auth(request):
    profile = get_profile_or_403(request=request)

    if not request.user.groups.filter(name='operator').exists() and not request.user.is_staff:
        return HttpResponseForbidden()
    user_login_history = UserLoginHistory.objects.order_by('-login_time')
    filter = UserFilter(request.GET, queryset=user_login_history)
    user_login_history = filter.qs
    table = UserTable(user_login_history)

    rows_per_page = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(table.rows, rows_per_page)
    try:
        table.page = paginator.page(page)
    except PageNotAnInteger:
        table.page = paginator.page(1)
    except EmptyPage:
        table.page = paginator.page(paginator.num_pages)

    return render(request, 'log/log.html', {'table': table, 'filter': filter})


@login_required
def log_app(request):
    profile = get_profile_or_403(request=request)

    if not request.user.groups.filter(name='operator').exists() and not request.user.is_staff and profile.company.status != 'ACTIVE' and request.user.groups.filter(name='observer').exists():
        return HttpResponseForbidden()

    if request.user.groups.filter(name='operator').exists():
        applications = Application.objects.order_by('-created_at')
    elif profile.company:
        lots = Lot.objects.exclude(Q(status='DRAFT') & ~Q(status='DELETED')).filter(company=profile.company).order_by(
            '-created_at')
        applications = Application.objects.exclude(status='WITHDRAWN').filter(lot__in=lots)

    filter = AppFilter(request.GET, queryset=applications)
    applications = filter.qs
    table = AppTable(applications)

    rows_per_page = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(table.rows, rows_per_page)
    try:
        table.page = paginator.page(page)
    except PageNotAnInteger:
        table.page = paginator.page(1)
    except EmptyPage:
        table.page = paginator.page(paginator.num_pages)

    return render(request, 'log/log.html', {'table': table, 'filter': filter})


@login_required
def log_result(request):
    profile = get_profile_or_403(request=request)

    if not request.user.groups.filter(
            name='operator').exists() and not request.user.is_staff and profile.company.status != 'ACTIVE' and request.user.groups.filter(
            name='observer').exists():
        return HttpResponseForbidden()
    lots = Lot.objects.exclude(Q(status='DRAFT') & ~Q(status='DELETED'))
    if request.user.groups.filter(name='operator').exists():
        result = Result.objects.order_by('-created_at')
    if profile.company:
        lots_customer = lots.filter(company=profile.company)
        result = Result.objects.filter(Q(lot__in=lots_customer) | (Q(lot__in=lots) & Q(bid__broker=profile.company))).order_by('-created_at')
    filter = ResultFilter(request.GET, queryset=result)
    result = filter.qs
    table = ResultTable(result)

    rows_per_page = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(table.rows, rows_per_page)
    try:
        table.page = paginator.page(page)
    except PageNotAnInteger:
        table.page = paginator.page(1)
    except EmptyPage:
        table.page = paginator.page(paginator.num_pages)
    return render(request, 'log/log.html', {'table': table, 'filter': filter})


def download_report(request, name):
    profile = get_profile_or_403(request=request)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    if name == 'log_auth':
        headers = ["ID", "Идентификация участника торгов", "Компания (БИН)", "Вход в систему участника торгов",
                   "Выход из системы участника торгов"]
        sheet.append(headers)
        user_login_history = UserLoginHistory.objects.order_by('-login_time')
        filter = UserFilter(request.GET, queryset=user_login_history)
        user_login_history = filter.qs
        for history in user_login_history:
            row_data = [
                history.id,
                history.user.username,
                history.company.idn if history.company else "--",
                str(history.login_time),
                str(history.logout_time) if history.logout_time else "--"
            ]
            sheet.append(row_data)
    elif name == 'log_app':
        headers = ["ID", "Дата и время открытие торга", "Время выставления заявки", "Номер торга", "Наименование",
                   "Количество лотов",
                   "Количество актива (объем)", "Цена", "Сумма", "Статус", "Брокер", "Участник", "БИН участника",
                   "Способ закупа"]
        sheet.append(headers)
        if request.user.groups.filter(name='operator').exists():
            applications = Application.objects.order_by('-created_at')
        elif profile.company:
            lots = Lot.objects.exclude(Q(status='DRAFT') & ~Q(status='DELETED')).filter(
                company=profile.company).order_by(
                '-created_at')
            applications = Application.objects.exclude(status='WITHDRAWN').filter(lot__in=lots)

        filter = AppFilter(request.GET, queryset=applications)
        applications = filter.qs
        for app in applications:
            row_data = [
                app.id,
                str(app.lot.bidding_begin),
                str(app.created_at),
                app.lot.number,
                app.lot.name,
                '1',
                sum(position.quantity for position in app.lot.positions.all()),
                sum(position.price for position in app.lot.positions.all()),
                sum(position.sum for position in app.lot.positions.all()),
                app.get_status_display(),
                app.lot.company.name,
                app.client.name,
                app.lot.company.idn,
                app.lot.get_type_display()
            ]
            sheet.append(row_data)
    elif name == 'log_result':
        headers = ["ID", "Дата и время открытие торга", "Дата и время закрытия торга", "Дата и время совершения сделки",
                   "Номер", "Наименование", "Количество лотов",
                   "Количество актива (объем)", "Цена", "Сумма", "Статус", "Брокер продавца", "Продавец",
                   "БИН Продавца", "Брокер покупателя", "Покупатель", "БИН покупателя", "Способ закупа"]
        sheet.append(headers)
        lots = Lot.objects.exclude(Q(status='DRAFT') & ~Q(status='DELETED'))
        if request.user.groups.filter(name='operator').exists():
            result = Result.objects.order_by('-created_at')
        if profile.company:
            lots_customer = lots.filter(company=profile.company)
            result = Result.objects.filter(
                Q(lot__in=lots_customer) | (Q(lot__in=lots) & Q(bid__broker=profile.company))).order_by('-created_at')

        filter = ResultFilter(request.GET, queryset=result)
        results = filter.qs
        for result in results:
            row_data = [
                result.id,
                str(result.lot.bidding_begin),
                str(result.lot.bidding_end),
                str(result.lot.bidding_end),
                result.lot.number,
                result.lot.name,
                '1',
                sum(position.quantity for position in result.lot.positions.all()),
                sum(position.price for position in result.lot.positions.all()),
                sum(position.sum for position in result.lot.positions.all()),
                result.get_status_display(),
                result.lot.company.name,
                result.lot.client.name,
                result.lot.client.idn,
                result.bid.broker.name if result.bid else "--",
                result.bid.participant.name if result.bid else "--",
                result.bid.participant.idn if result.bid else "--",
                result.lot.get_type_display()
            ]
            sheet.append(row_data)

    for col in sheet.columns:  # для ширины столцов
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        sheet.column_dimensions[column].width = adjusted_width

    file_name = name + '.xlsx'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    workbook.save(response)

    return response


@login_required
def download_result(request):
    profile = get_profile_or_403(request=request)
    datetime_open_auction = request.GET.get('datetime_open_auction')
    datetime_close_auction = request.GET.get('datetime_close_auction')

    if not datetime_open_auction or not datetime_close_auction:
        messages.add_message(request, messages.WARNING, 'Введите период.')
        return redirect('log_result')


    start_date = datetime.strptime(datetime_open_auction, '%d.%m.%Y')
    end_date = datetime.strptime(datetime_close_auction, '%d.%m.%Y')

    lots = Lot.objects.filter(bidding_end__range=(start_date, end_date),status__in=['COMPLETED', 'NOT_COMPLETED', 'CANCELLED', 'REVOKED'])
    if request.user.groups.filter(name='operator').exists():
        result = Result.objects.order_by('-created_at')
    if profile.company:
        lots_customer = lots.filter(company=profile.company)
        result = Result.objects.filter(
            Q(lot__in=lots_customer) | (Q(lot__in=lots) & Q(bid__broker=profile.company))).order_by('-created_at')

    # Создаем объект для записи в память
    zip_buffer = io.BytesIO()

    # Создаем ZIP-архив
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for lot in lots:
            if result.filter(lot=lot).exists():
                position = lot.positions.filter(status='ACTIVE').first()
                applications = lot.applications.exclude(status='WITHDRAWN').exclude(status='REJECTED').all()
                bids = lot.bids.order_by('-created_at').all()

                url = 'https://nationalbank.kz/rss/get_rates.cfm?fdate=%s' % (lot.bidding_end.strftime('%d.%m.%Y'))

                response_xml = requests.get(url)
                xml_data = response_xml.content
                exchange = ET.fromstring(xml_data)
                cny, eur, usd, rub = services.get_exchange(exchange)

                qr_codes = services.get_qr_codes(signature=lot.result.signature)
                sum_with_vat,sum_without_vat = '', ''
                if lot.result.bid:
                    sum = float(lot.result.bid.sum)
                    if lot.vat is True:
                        sum_with_vat = Decimal(sum).quantize(Decimal(10) ** -2)
                        sum_without_vat = Decimal(sum / 1.12).quantize(Decimal(10) ** -2)
                    else:
                        sum_with_vat = Decimal(sum * 1.12).quantize(Decimal(10) ** -2)
                        sum_without_vat = Decimal(sum).quantize(Decimal(10) ** -2)


                filename = f"Отчет_{lot.number}.pdf"
                html_content = render_to_string('standard/reports/result.html',
                                                {'lot': lot,
                                                'position': position,
                                                'applications':applications,
                                                'bids': bids,
                                                'sum_with_vat': sum_with_vat,
                                                'sum_without_vat': sum_without_vat,
                                                'img':qr_codes,
                                                'cny':cny, 'eur':eur, 'usd':usd, 'rub':rub})


                pdf_content = io.BytesIO()
                pisa.CreatePDF(html_content, dest=pdf_content)


                zip_file.writestr(filename, pdf_content.getvalue())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="Отчеты_по_биржевым_сделкам.zip"'
    return response
