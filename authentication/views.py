from cryptography import x509
import ssl
import re
import random
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.utils.translation import gettext

from authentication.forms import NewUserForm, CertificateForm, CompanyForm
from authentication.helpers import get_profile_or_403
from authentication.models import Profile
from clearing.models import Wallet
from clearing.views import get_wallet, wallet, create_company


class UpdateLoginView(LoginView):
    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Логин и пароль не совпадают. Пожалуйста, попробуйте еще.")
        return redirect('auth_signature')


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, gettext('Аккаунт создан.'))
            Profile.objects.create(user=user)
            return redirect('home_page')
        else:
            for field in form.errors:
                messages.add_message(request, messages.WARNING, form.errors[field].as_text())
            # return redirect('auth_signature')
    else:
        form = NewUserForm()
    return render(request=request, template_name="registration/register.html", context={"form": form})


def auth_signature(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            xml = form.data['signature']
            begin = xml.find('<ds:X509Certificate>')
            end = xml.find('</ds:X509Certificate>')

            cert_string = '-----BEGIN CERTIFICATE-----' + xml[begin + 20:end] + '-----END CERTIFICATE-----'

            cert = x509.load_pem_x509_certificate(cert_string.encode('utf-8'))
            import datetime
            if cert.not_valid_after >= datetime.datetime.now():
                subject = ''
                for attr in cert.subject:
                    subject += ssl._txt2obj(attr.oid.dotted_string)[1] + '=' + attr.value + ' '
                subject = subject[:-1]
                bin = re.search(r"OU=BIN(\d+)", subject).group(1)
                idn = re.search(r"serialNumber=IIN(\d+)", subject).group(1)
                username = idn + '_' + bin
                profile = Profile.objects.filter(user__username=username).exists()
                if profile:
                    profile = Profile.objects.get(user__username=username)
                    return render(request, 'registration/login.html', {'profile': profile.user.username})
                else:
                    form = NewUserForm()
                    return render(request, 'registration/register.html', {"form": form, 'idn': idn, 'username': username,'cert': subject})
            else:
                form = CertificateForm()
                return render(request, 'registration/signature.html', {'form': form})
    else:
        form = CertificateForm()
    return render(request, 'registration/signature.html', {'form': form})

@login_required
@permission_required('company.view_company')
def profile(request):
    profile = get_profile_or_403(request=request)
    company = profile.company
    # if company.clearing_code:
    #     get_wallet(company.idn)
    return render(request, 'registration/profile.html', {'company': company})

@login_required
def add_company(request):
    if request.user.profile is None:
        return redirect('auth_register')
    if request.user.profile.company:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            idn = form.cleaned_data['idn']
            # bin = re.search(r"OU=BIN(\d+)", request.user.profile.signature).group(1)
            # if idn == bin:
            company = form.save(commit=False)
            if company.type == 'OBSERVER':
                group = Group.objects.get(name='observer')
                request.user.groups.add(group)
            elif company.type == 'TRADER':
                # response = wallet(company.idn)
                # if not response:
                #     data = {'type': 'TRADER',
                #             'name': company.name,
                #             'bin': company.idn,
                #             'address': company.address,
                #             'email': company.email
                #             }
                #     response_clearing = create_company(data)
                #     if response_clearing:
                #         response = wallet(company.idn)
                #     else:
                #         messages.add_message(request, messages.SUCCESS, gettext('Ошибка клиринга.'))
                #         return render(request, 'registration/company_add.html', {'form': form})
                # if company.type == 'TRADER':
                #     Wallet.objects.create(idn=company.idn,
                #                           account_number=response['account_number'],
                #                           currency_code=response['currency_code'],
                #                           deposited_amount=response['deposited_amount'],
                #                           holding_amount=response['holding_amount'],
                #                           locked_amount=response['locked_amount'],
                #                           available_amount=response['available_amount'],
                #                           )
                company.status = 'PENDING'
                company.created_by = request.user
                company.updated_by = request.user
                company.exchange_id = random.randint(100000, 999999)
                company.full_clean()
                company.save()

                request.user.profile.company = company
                request.user.profile.save()

                messages.add_message(request, messages.SUCCESS, gettext('Компания создана.'))
                return render(request, 'company/pages/company_profile.html', {'company': request.user.profile.company})
            # else:
            #     messages.add_message(request, messages.SUCCESS, 'БИН не совпадает с БИН в ЭЦП. Попробуйте еще раз.')
            #     form = CompanyForm()
    else:
        form = CompanyForm()
    return render(request, 'registration/company_add.html', {'form': form})
