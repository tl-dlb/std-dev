import json
import requests
from decimal import Decimal
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import get_template

import xml.etree.ElementTree as ET

from authentication.helpers import get_profile_or_403
from standard.models import Lot

from files.models import File
from files.report import create_daily_report
from files import helpers

from ..forms import UploadFileForm, ReportForm
from .. import services

from xhtml2pdf import pisa


@login_required
@permission_required('files.add_file')
def upload(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.company != profile.company:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = File(
                field      = request.FILES['file'], 
                name       = request.FILES['file'], 
                type       = form.data['type'], 
                created_by = request.user,
                #updated_by = request.user,
            )  
            instance.save()
            lot.files.add(instance)
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = UploadFileForm()
    return render(request, 'standard/pages/file_upload.html', {'lot':lot, 'form':form})


@login_required
@permission_required('files.delete_file')
def delete(request, uuid, file_id):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.company != profile.company :
        return HttpResponseForbidden()

    file = get_object_or_404(File, pk=file_id)
    lot.files.remove(file)
    return redirect('lot_detail', uuid=lot.uuid)


@login_required
@permission_required('files.view_file')
def admission(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.status not in ('ADMITTED','BIDDING','COMPLETED','NOT_COMPLETED','CANCELLED','REVOKED'):
        return HttpResponseForbidden()

    position = lot.positions.filter(status='ACTIVE').first()
    applications = lot.applications.exclude(status='WITHDRAWN').all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Реестр заявок участников.pdf"'

    template = get_template('standard/reports/admission.html')
    html = template.render({'lot':lot, 'position':position, 'applications':applications})

    pisaStatus = pisa.CreatePDF(
        html.encode("UTF-8"), 
        dest=response, 
        encoding='UTF-8', 
        link_callback=helpers.fetch_pdf_resources
    )

    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err, html))
    return response


@login_required
@permission_required('files.view_file')
def result(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.status not in ('COMPLETED', 'NOT_COMPLETED', 'CANCELLED', 'REVOKED'):
        return HttpResponseForbidden()

    position = lot.positions.filter(status='ACTIVE').first()
    applications = lot.applications.exclude(status='WITHDRAWN').exclude(status='REJECTED').all()
    bids = lot.bids.order_by('-created_at').all()

    url = 'https://nationalbank.kz/rss/get_rates.cfm?fdate=%s' % (lot.bidding_end.strftime('%d.%m.%Y'))

    response_xml = requests.get(url)
    xml_data = response_xml.content 
    exchange = ET.fromstring(xml_data)
    cny, eur, usd, rub = services.get_exchange(exchange)

    qr_codes = services.get_qr_codes(signature=lot.result.signature)

    sum = float(lot.result.bid.sum)
    if lot.vat is True:
        sum_with_vat = Decimal(sum).quantize(Decimal(10) ** -2)
        sum_without_vat = Decimal(sum / 1.12).quantize(Decimal(10) ** -2)
    else:
        sum_with_vat = Decimal(sum * 1.12).quantize(Decimal(10) ** -2)
        sum_without_vat = Decimal(sum).quantize(Decimal(10) ** -2)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Отчет по биржевой сделке.pdf"'

    template = get_template('standard/reports/result.html')
    html = template.render({
        'lot': lot,
        'position': position,
        'applications':applications,
        'bids': bids,
        'sum_with_vat': sum_with_vat,
        'sum_without_vat': sum_without_vat,
        'img':qr_codes,
        'cny':cny, 'eur':eur, 'usd':usd, 'rub':rub
    })

    pisaStatus = pisa.CreatePDF(
        html.encode("UTF-8"), 
        dest=response, 
        encoding='UTF-8', 
        link_callback=helpers.fetch_pdf_resources
    )

    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err, html))
    return response


@login_required
@permission_required('files.view_file')
def progress(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.status not in ('COMPLETED'):
        return HttpResponseForbidden()

    bids = lot.bids.order_by('-created_at').all()

    qr_codes = services.get_qr_codes(signature=lot.result.signature)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Ценовые предложения участников.pdf"'

    template = get_template('standard/reports/progress.html')
    html = template.render({'lot':lot, 'bids': bids, 'img':qr_codes})

    pisaStatus = pisa.CreatePDF(
        html.encode("UTF-8"), 
        dest=response, 
        encoding='UTF-8', 
        link_callback=helpers.fetch_pdf_resources
    )

    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err, html))
    return response


#REPORT 
@login_required
@permission_required('files.view_file')
def report(request):
    profile = get_profile_or_403(request=request)

    if not request.user.groups.filter(name='operator').exists() and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.POST:
        form = ReportForm(request.POST)
        if form.is_valid():
            stream = create_daily_report(form.data['start_date'], form.data['end_date'])
            response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=report' + str(form.data['start_date']) + '-' + str(form.data['end_date']) + '.xlsx'
            return response
    else:
        form = ReportForm()
    return render(request, 'standard/pages/report_create.html', {'form':form})
