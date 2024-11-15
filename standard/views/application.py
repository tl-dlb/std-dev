from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext

from authentication.helpers import get_profile_or_403
from clearing.models import Wallet, Statement
from clearing.views import get_wallet, hold, free

from standard.models import Lot, Application
from company.models import Company
from files.models import File
from events.models import Event
from ..forms import ApplicationForm, CommentForm
from .. import selectors
from .. import services



#CREATE APPLICATION 
@login_required
@permission_required('standard.add_application')
def create(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'SUBMISSION':
        return HttpResponseForbidden()
    if lot.status == 'SUBMISSION' and lot.company == profile.company:
        return HttpResponseForbidden()
    if lot.applications.filter(company=profile.company).exclude(status='WITHDRAWN').first():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ApplicationForm(request.user, lot, request.POST, request.FILES)
        if form.is_valid():
            client = get_object_or_404(Company, pk=form.data['client'])

            if lot.applications.filter(client=client).exclude(status='WITHDRAWN').first():
                messages.add_message(request, messages.WARNING, gettext('От имени данного клиента уже была подана заявка.'))
                return redirect('lot_application_create', uuid=lot.uuid)
            if lot.guarantee:
                if form.cleaned_data['use_client_guarantee']:
                    get_wallet(idn=client.idn)
                    balance = Wallet.objects.get(idn=client.idn).available_amount
                else:
                    get_wallet(idn=profile.company.idn)
                    balance = Wallet.objects.get(idn=profile.company.idn).available_amount
                if balance < lot.guarantee_amount_sum:
                    messages.add_message(request, messages.WARNING, gettext('Отсутствуют средства на счету гарантийного обеспечения.'))
                    return redirect('lot_application_create', uuid=lot.uuid)
                        
            application = Application(
                lot=lot,
                company=profile.company,
                client=client,
                status='PENDING',
                created_by=request.user,
                updated_by=request.user,
            )
            application.full_clean()
            application.save()
            
            if 'file' in request.FILES:
                instance = File(
                    field      = request.FILES['file'], 
                    name       = request.FILES['file'], 
                    type       = 'APPLICATION', 
                    created_by = request.user,
                    #updated_by = request.user,
                )  
                instance.save()
                application.files.add(instance)

            if lot.guarantee:
                if form.cleaned_data['use_client_guarantee']:
                    hold(id=lot.uuid, number=lot.number, idn=client.idn, amount=lot.guarantee_amount_sum) #заморозка у клиента
                    get_wallet(idn=client.idn)
                else:
                    hold(id=lot.uuid, number=lot.number, idn=profile.company.idn, amount=lot.guarantee_amount_sum)  # заморозка у брокера
                    get_wallet(idn=profile.company.idn)
            messages.add_message(request, messages.SUCCESS, gettext('Заявка подана.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = ApplicationForm(request.user, lot)

    return render(request, 'standard/pages/application_create.html', {'lot':lot, 'form':form})


#DELETE APPLICATION 
@login_required
@permission_required('standard.delete_application')
def delete(request, uuid, app_id):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'SUBMISSION':
        return HttpResponseForbidden()

    application = get_object_or_404(Application, pk=app_id)

    if application.status != 'PENDING':
        return HttpResponseForbidden()
    if application.company != profile.company:
        return HttpResponseForbidden()

    application.status = 'WITHDRAWN'
    application.full_clean()
    application.save()
    
    if lot.guarantee:
        # вернуть и обновить
        idn = application.company.idn
        account_number = get_wallet(idn)
        statements = Statement.objects.filter(id_app=lot.uuid).filter(type='HOLDING').exclude(is_active=False)
        statement_exists = statements.filter(account_number=account_number).exists()
        if not statement_exists:
            idn = application.client.idn
            account_number = get_wallet(idn)
        id = statements.get(account_number=account_number).id_operation
        free(lot.uuid, account_number.account_number, id)
        get_wallet(idn)
    messages.add_message(request, messages.SUCCESS, gettext('Заявка отозвана.'))
    return redirect('lot_detail', uuid=lot.uuid)


#ADMIT APPLICATION
@login_required
@permission_required('standard.change_application')#
def admit(request, uuid, app_id):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'ADMISSION':
        return HttpResponseForbidden()
    if lot.company != profile.company and not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()
    
    application = get_object_or_404(Application, pk=app_id)

    if application.status not in ('PENDING', 'REJECTED'):
        return HttpResponseForbidden()
    
    application.status = 'ADMITTED'
    application.full_clean()
    application.save()

    messages.add_message(request, messages.SUCCESS, gettext('Заявка допущена.'))
    return redirect('lot_detail', uuid=lot.uuid)


#REJECT APPLICATION
@login_required
@permission_required('standard.change_application')#
def reject(request, uuid, app_id):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'ADMISSION':
        return HttpResponseForbidden()
    if lot.company != profile.company and not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()
    
    application = get_object_or_404(Application, pk=app_id)

    if application.status not in ('PENDING', 'ADMITTED'):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            application.status = 'REJECTED'
            application.full_clean()
            application.save()

            event = Event.objects.create(
                type='REJECTED', 
                comment=form.data['comment'], 
                created_by=request.user
            )
            event.full_clean()
            event.save()

            application.events.add(event)
            
            if lot.guarantee:
                # вернуть и обновить
                idn = application.company.idn
                account_number = get_wallet(idn)  # обновление
                statements = Statement.objects.filter(id_app=lot.uuid).filter(type='HOLDING').exclude(is_active=False)
                statement_exists = statements.filter(account_number=account_number).exists()
                if not statement_exists:
                    idn = application.client.idn
                    account_number = get_wallet(idn)
                id = statements.get(account_number=account_number).id_operation
                free(lot.uuid, account_number.account_number, id)
                get_wallet(idn)
            messages.add_message(request, messages.SUCCESS, gettext('Заявка отклонена.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = CommentForm()

    return render(request, 'standard/pages/application_reject.html', {'lot':lot, 'application':application, 'form':form})
