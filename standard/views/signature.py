from cryptography import x509
import ssl
import re
import random
import datetime
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext

from authentication.helpers import get_profile_or_403
from standard.models  import Lot
from ..forms import SignatureForm


#CREATE SIGNATURE
@login_required
@permission_required('signature.add_signature')
def create(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'SUMMARIZING':
        return HttpResponseForbidden()
    if not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()

    result = lot.result
    if not result:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = SignatureForm(request.POST)
        if form.is_valid():
            xml = form.data['data']
            begin = xml.find('<ds:X509Certificate>')
            end = xml.find('</ds:X509Certificate>')
            cert_string = '-----BEGIN CERTIFICATE-----' + xml[begin + 20:end] + '-----END CERTIFICATE-----'
            cert = x509.load_pem_x509_certificate(cert_string.encode('utf-8'))

            if cert.not_valid_after >= datetime.datetime.now():
                subject = ''
                for attr in cert.subject:
                    subject += ssl._txt2obj(attr.oid.dotted_string)[1] + '=' + attr.value + ' '
                subject = subject[:-1]
                name = re.search(r'CN=([^=]+?)\s+SN', subject).group(1)
                company = re.search(r'O=([^=]+?)\s+OU', subject).group(1)
                bin = re.search(r'OU=(\w+)', subject).group(1)
                signature = form.save(commit=False)
                signature.type        = 'RESULT'
                signature.status      = 'VALID'
                signature.created_by  = request.user
                signature.value       = subject
                signature.certificate = cert_string
                signature.name = name
                signature.company = company
                signature.bin = bin
                signature.full_clean()
                signature.save()

                result.signature = signature
                result.full_clean()
                result.save()

                messages.add_message(request, messages.SUCCESS, gettext('Итоги подписаны.'))
                return redirect('lot_detail', uuid=lot.uuid)
            else:
                form = SignatureForm()
                messages.add_message(request, messages.SUCCESS, gettext('ЭЦП с истекшим сроком годности'))
                return render(request, 'standard/pages/signature_create.html', {'lot': lot, 'form': form})
    else:
        form = SignatureForm()
    return render(request, 'standard/pages/signature_create.html', {'lot':lot, 'form':form})
