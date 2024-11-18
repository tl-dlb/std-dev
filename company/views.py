from django.utils import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext
from django_tables2.config import RequestConfig
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from authentication.helpers import get_profile_or_403
from clearing.models import Wallet
from clearing.views import wallet, get_wallet, create_company, create_client
from .models import Company
from .forms import CompanyForm
from .filters import CompanyFilterForm
from .tables import ClientTable, TraderTable
from . import selectors

from integration.requests import company_create


# LIST OF CLIENTS
@login_required
@permission_required('company.view_company')
def list(request):
    profile = get_profile_or_403(request=request)
    clients = selectors.get_clients(request=request)
    # for client in clients:
    #     get_wallet(client.idn)
    table = ClientTable(clients)

    rows_per_page = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(table.rows, rows_per_page)
    try:
        table.page = paginator.page(page)
    except PageNotAnInteger:
        table.page = paginator.page(1)
    except EmptyPage:
        table.page = paginator.page(paginator.num_pages)

    form = CompanyFilterForm(request.GET)
    return render(request, 'company/pages/client_list.html', {'form': form, 'table': table})


# CREATE, ADD CLIENT
@login_required
@permission_required('company.add_company')
def create(request):
    profile = get_profile_or_403(request=request)

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            # response = wallet(company.idn)
            # if not response:
            #     data = {'type': 'CLIENT',
            #             'name': company.name,
            #             'bin': company.idn,
            #             'address': company.address,
            #             'email': company.email
            #             }
            #     response_clearing = create_client(data,profile.company.idn)
            #     if response_clearing:
            #         response = wallet(company.idn)
            #     else:
            #         messages.add_message(request, messages.SUCCESS, gettext('Ошибка клиринга.'))
            #         return render(request, 'company/pages/client_create.html', {'form': form})

            company.status = 'PENDING'
            company.created_by = request.user
            company.updated_by = request.user
            company.save()
            profile.company.clients.add(company)
            # Wallet.objects.create(idn=company.idn,
            #                       account_number=response['account_number'],
            #                       currency_code=response['currency_code'],
            #                       deposited_amount=response['deposited_amount'],
            #                       holding_amount=response['holding_amount'],
            #                       locked_amount=response['locked_amount'],
            #                       available_amount=response['available_amount'],
            #                       )
            messages.add_message(request, messages.SUCCESS,
                                 gettext('Компания создана и добавлена к вашему списку клиентов. Ожидается подтверждение.'))
            return redirect('client_detail', id=company.id)

        elif form.data.get('idn'):
            company = Company.objects.filter(idn=form.data.get('idn')).first()
            if company:
                if not profile.company.clients.filter(id=company.id).exists():
                    profile.company.clients.add(company)
                    messages.add_message(request, messages.SUCCESS,
                                         gettext('Компания с таким БИН/ИИН добавлена к вашему списку клиентов из существующей базы данных.'))
                    return redirect('client_detail', id=company.id)
                else:
                    messages.add_message(request, messages.WARNING,
                                         gettext('Компания с таким БИН/ИИН уже была добавлена к вашему списку клиентов.'))
                    return redirect('client_detail', id=company.id)

    else:
        form = CompanyForm()
    return render(request, 'company/pages/client_create.html', {'form': form})


# VIEW CLIENT
@login_required
@permission_required('company.view_company')
def detail(request, id):
    profile = get_profile_or_403(request=request)
    company = get_object_or_404(Company, pk=id)
    # get_wallet(company.idn)
    traders = company.clients.all()
    trader_table = TraderTable(traders)
    return render(request, 'company/pages/client_detail.html', {'company': company, 'table': trader_table})


# EDIT CLIENT
@login_required
@permission_required('company.change_company')
def edit(request, id):
    profile = get_profile_or_403(request=request)
    company = get_object_or_404(Company, pk=id)

    if request.POST:
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            company = form.save(commit=False)
            company.updated_by = request.user
            company.updated_at = timezone.now()
            company.full_clean()
            company.save()
            messages.add_message(request, messages.SUCCESS, gettext('Изменения сохранены.'))
            return redirect('client_detail', id=company.id)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'company/pages/client_edit.html', {'company': company, 'form': form})


# ADMIT CLIENT
@login_required
@permission_required('company.change_company')
def admit(request, id):
    profile = get_profile_or_403(request=request)
    company = get_object_or_404(Company, pk=id)

    if company.status in ('ACTIVE'):
        return HttpResponseForbidden()

    company.status = 'ACTIVE'
    company.full_clean()
    company.save()

    # company_create(company)

    messages.add_message(request, messages.SUCCESS, gettext('Компания активирована.'))
    return redirect('client_detail', id=company.id)


@login_required
@permission_required('company.change_company')
def block(request, id):
    profile = get_profile_or_403(request=request)
    company = get_object_or_404(Company, pk=id)

    if company.status in ('BLOCKED'):
        return HttpResponseForbidden()

    company.status = 'BLOCKED'
    company.full_clean()
    company.save()


    messages.add_message(request, messages.SUCCESS, gettext('Компания заблокирована.'))
    return redirect('client_detail', id=company.id)

# VIEW COMPANY
@login_required
@permission_required('company.view_company')
def profile(request):
    profile = get_profile_or_403(request=request)
    company = profile.company
    return render(request, 'company/pages/company_profile.html', {'company': company})