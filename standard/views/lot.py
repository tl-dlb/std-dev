import requests
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext
from django_tables2 import RequestConfig
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from authentication.helpers import get_profile_or_403
from clearing.models import Wallet, Statement
from clearing.views import get_wallet, free, lock, hold, deal
from config.settings import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY
from counter.selectors import get_counter_last_number
from counter.services import increment_counter_last_number

from standard.models  import Lot #TODO: move to data
from company.models import Company
from events.models import Event

from ..filters import LotFilterForm
from ..forms   import LotForm, CommentForm
from ..tables  import LotTable, ApplicationTable

from .. import selectors
from .. import services

from integration.requests import lot_publish, lot_result


#LIST OF LOTS
@login_required
@permission_required('standard.view_lot')
def list(request):
    profile = get_profile_or_403(request=request)
    lots = selectors.get_lots(request=request)
    table = LotTable(lots)
    RequestConfig(request=request).configure(table)

    rows_per_page = 25
    page = request.GET.get('page', 1)
    paginator = Paginator(table.rows, rows_per_page)
    try:
        table.page = paginator.page(page)
    except PageNotAnInteger:
        table.page = paginator.page(1)
    except EmptyPage:
        table.page = paginator.page(paginator.num_pages)

    form = LotFilterForm(request.GET)
    return render(request, 'standard/pages/lot_list.html', {'form':form, 'table':table})


#CREATE LOT
@login_required
@permission_required('standard.add_lot')
def create(request):
    profile = get_profile_or_403(request=request)
    if request.method == 'POST':
        form = LotForm(request.user, request.POST)
        if form.is_valid():
            client = get_object_or_404(Company, pk=form.data['client'])

            lot = form.save(commit=False)
            lot.number     = 'СТАНД' + str(get_counter_last_number(type='STANDARD') + 1).zfill(6)
            lot.status     = 'DRAFT'
            lot.created_by = request.user
            lot.updated_by = request.user
            lot.company    = profile.company
            lot.client     = client
            if form.cleaned_data['guarantee'] is False:
                lot.guarantee_amount = 0
            lot.full_clean()
            lot.save()

            increment_counter_last_number(type='STANDARD')
            services.set_bidding_end(lot=lot)
            messages.add_message(request, messages.SUCCESS, gettext('Лот создан.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = LotForm(request.user)
    return render(request, 'standard/pages/lot_create.html', {'form':form})


#VIEW LOT
@login_required
@permission_required('standard.view_lot')
def detail(request, uuid):
    profile = get_profile_or_403(request=request)
    lot     = get_object_or_404(Lot, uuid=uuid)
    visible = lot.company == profile.company or request.user.groups.filter(name='operator').exists()

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status == 'DELETED':
        return HttpResponseForbidden()
    if lot.status == 'DRAFT' and not lot.company == profile.company:
        return HttpResponseForbidden()

    position   = lot.positions.filter(status='ACTIVE').first()
    apps       = lot.applications.exclude(status='WITHDRAWN')
    apps_count = apps.count()

    admission = False
    if not visible:
        apps = apps.filter(company=profile.company)
        if apps.filter(status='ADMITTED').exists():
            admission = True

    apps_table = ApplicationTable(apps)
    if request.POST:
        if lot.status in 'BIDDING,SUMMARIZING,COMPLETED,NOT_COMPLETED,REVOKED' and visible or admission:
            captcha_response = request.POST.get('g-recaptcha-response')
            if captcha_response:
                data = {
                    'secret': RECAPTCHA_PRIVATE_KEY,
                    'response': captcha_response,
                }
                verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                verify_result = verify_response.json()
                if not verify_result.get('success', False):
                    messages.add_message(request, messages.WARNING, gettext('Ошибка CAPTCHA. Пожалуйста, повторите попытку.'))
                    return redirect('lot_detail', uuid=lot.uuid)
                else:
                    return redirect('lot_bid_list', uuid=lot.uuid)
            else:
                messages.add_message(request, messages.WARNING, gettext('Ошибка CAPTCHA. Пожалуйста, повторите попытку.'))
                return redirect('lot_detail', uuid=lot.uuid)

    return render(request, 'standard/pages/lot_detail.html', {
        'visible'   : visible,
        'admission' : admission,
        'lot'       : lot,
        'position'  : position,
        'apps'      : apps,
        'apps_count': apps_count,
        'apps_table': apps_table,
        'public_key': RECAPTCHA_PUBLIC_KEY
    })


#EDIT LOT
@login_required
@permission_required('standard.change_lot')
def edit(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status not in ('DRAFT', 'PUBLISHED', 'SUBMISSION'):
        return HttpResponseForbidden()
    if lot.company != profile.company:
        return HttpResponseForbidden()

    if request.POST:
        form = LotForm(request.user, request.POST, instance=lot)
        if form.is_valid():
            lot = form.save(commit=False)
            lot.updated_by = request.user
            lot.updated_at = timezone.now()
            if 'guarantee' in form.data and form.cleaned_data['guarantee'] is False:
                lot.guarantee_amount = 0
            lot.full_clean()
            lot.save()

            services.set_bidding_end(lot=lot)

            if 'comment' in form.data:
                event = Event.objects.create(
                    type='CHANGED',
                    comment=form.data['comment'],
                    created_by=request.user
                )
                event.full_clean()
                event.save()
                lot.events.add(event)

            messages.add_message(request, messages.SUCCESS, gettext('Изменения сохранены.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = LotForm(request.user, instance=lot)
    return render(request, 'standard/pages/lot_edit.html', {'lot':lot, 'form':form})


#DELETE LOT
@login_required
@permission_required('standard.delete_lot')
def delete(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'DRAFT':
        return HttpResponseForbidden()
    if lot.company != profile.company:
        return HttpResponseForbidden()

    lot.status = 'DELETED'
    lot.full_clean()
    lot.save()

    messages.add_message(request, messages.SUCCESS, gettext('Лот удален.'))
    return redirect('lot_list')


#PUBLISH LOT
@login_required
@permission_required('standard.change_lot')
def publish(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'DRAFT':
        return HttpResponseForbidden()
    if lot.company != profile.company:
        return HttpResponseForbidden()

    if lot.submission_begin < timezone.now():
        messages.add_message(request, messages.WARNING, gettext('Начало приема заявок не может быть в прошлом.'))
        return redirect('lot_detail', uuid=lot.uuid)
    if lot.submission_end < timezone.now():
        messages.add_message(request, messages.WARNING, gettext('Окончание приема заявок не может быть в прошлом.'))
        return redirect('lot_detail', uuid=lot.uuid)
    if lot.bidding_begin < timezone.now():
        messages.add_message(request, messages.WARNING, gettext('Начало аукциона не может быть в прошлом.'))
        return redirect('lot_detail', uuid=lot.uuid)
    if lot.sum == 0:
        messages.add_message(request, messages.WARNING, gettext('Добавьте позицию.'))
        return redirect('lot_detail', uuid=lot.uuid)
    if not lot.files.filter(type='SPEC').all():
        messages.add_message(request, messages.WARNING, gettext('Загрузите техническую спецификацию.'))
        return redirect('lot_detail', uuid=lot.uuid)
    if not lot.files.filter(type='CONTRACT').all():
        messages.add_message(request, messages.WARNING, gettext('Загрузите шаблон договора.'))
        return redirect('lot_detail', uuid=lot.uuid)

    if lot.guarantee:

        get_wallet(idn=profile.company.idn)  # обновление
        balance = Wallet.objects.get(idn=profile.company.idn).available_amount  # проврка
        if balance < lot.guarantee_amount_sum:
            messages.add_message(request, messages.WARNING, gettext('Отсутствуют средства на счету гарантийного обеспечения.'))
            return redirect('lot_detail', uuid=lot.uuid)
        hold(id=lot.uuid, number=lot.number, idn=profile.company.idn, amount=lot.guarantee_amount_sum)  # заморозка
        get_wallet(idn=profile.company.idn)



    lot.status = 'PUBLISHED'
    lot.full_clean()
    lot.save()

    # lot_publish(lot) TODO

    messages.add_message(request, messages.SUCCESS, gettext('Лот опубликован.'))
    return redirect('lot_detail', uuid=lot.uuid)



#ADMIT APPLICATIONS OF LOT
@login_required
@permission_required('standard.change_lot')
def admit(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'ADMISSION':
        return HttpResponseForbidden()
    if lot.company != profile.company and not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()

    pending_applications = lot.applications.filter(status='PENDING').all()
    if pending_applications:
        messages.add_message(request, messages.WARNING, gettext('Примите решение по всем заявкам.'))
        return redirect('lot_detail', uuid=lot.uuid)

    admitted_applications = lot.applications.filter(status='ADMITTED').all()
    if admitted_applications.count() < 2 and lot.type == 'AUCTION_DOWN':
        lot.status = 'SUMMARIZING'
        lot.full_clean()
        lot.save()

        messages.add_message(request, messages.SUCCESS, gettext('Лот переведен в статус "Подведение итогов".'))
        return redirect('lot_detail', uuid=lot.uuid)

    lot.status = 'ADMITTED'
    lot.full_clean()
    lot.save()

    messages.add_message(request, messages.SUCCESS, gettext('Участники определены.'))
    return redirect('lot_detail', uuid=lot.uuid)


#SUMMARIZE LOT
@login_required
@permission_required('standard.change_lot')
def summarize(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'SUMMARIZING':
        return HttpResponseForbidden()
    if not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()

    result = lot.result
    if not result and not result.signature:
        return HttpResponseForbidden()

    if lot.guarantee:

        statements = Statement.objects.filter(id_app=lot.uuid).filter(type='HOLDING').exclude(is_active=False)
        if result.status == 'HAS_WINNER':
            # блокировка брокера
            broker_idn = result.lot.company.idn
            account_number_broker = get_wallet(broker_idn)
            statement_broker = statements.get(account_number=account_number_broker)
            id_oper = statement_broker.id_operation
            lock(lot.uuid, account_number_broker.account_number, id_oper, number=lot.number)
            get_wallet(broker_idn)
            statements = statements.exclude(account_number=account_number_broker)
            # блокировка победителя
            idn=result.bid.participant.idn
            account_number = get_wallet(idn)
            statement_exists = statements.filter(account_number=account_number).exists()
            if not statement_exists:
                idn = result.bid.broker.idn
                account_number = get_wallet(idn)
            id = statements.get(account_number=account_number).id_operation
            lock(lot.uuid, account_number.account_number, id, number=lot.number)
            get_wallet(idn)
            statements = statements.exclude(account_number=account_number)
        for sup in statements:
            account_number = get_wallet(idn=sup.account_number.idn)
            free(lot.uuid, account_number.account_number, sup.id_operation)
            get_wallet(idn=sup.account_number.idn)
        blocked_amount_go = lot.guarantee_amount
    else:
        blocked_amount_go = 0

    lot.status = 'COMPLETED' if result.status == 'HAS_WINNER' else 'NOT_COMPLETED'
    lot.full_clean()
    lot.save()

    # lot_result(lot)
    if result.status == 'HAS_WINNER':
        deal(lot)
    messages.add_message(request, messages.SUCCESS, gettext('Итоги опубликованы.'))
    return redirect('lot_detail', uuid=lot.uuid)


#CANCEL LOT
@login_required
@permission_required('standard.change_lot')#
def cancel(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status not in ('PUBLISHED', 'SUBMISSION', 'ADMISSION', 'ADMITTED'):
        return HttpResponseForbidden()
    if not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():

            if lot.guarantee:
                # вернуть и обновить
                statements = Statement.objects.filter(id_app=lot.uuid).filter(type='HOLDING').exclude(is_active=False)
                applications = lot.applications.all()
                for application in applications:
                    idn = application.company.idn
                    account_number = get_wallet(idn)  # обновление
                    statement_exists = statements.filter(account_number=account_number).exists()
                    if not statement_exists:
                        idn = application.client.idn
                        account_number = get_wallet(idn)
                    id = statements.get(account_number=account_number).id_operation
                    free(lot.uuid, account_number.account_number, id)
                    get_wallet(idn)

            lot.status = 'CANCELLED'
            lot.full_clean()
            lot.save()

            event = Event.objects.create(
                type='CANCELLED',
                comment=form.data['comment'],
                created_by=request.user
            )
            event.full_clean()
            event.save()

            lot.events.add(event)

            messages.add_message(request, messages.SUCCESS, gettext('Лот отменен.'))
            return redirect('lot_detail', uuid=lot.uuid)
        else:
            messages.add_message(request, messages.SUCCESS, gettext('Ошибка.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = CommentForm()

    return render(request, 'standard/pages/lot_cancel.html', {'lot': lot, 'form': form})


#REVOKE LOT
@login_required
@permission_required('standard.change_lot')
def revoke(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)
    operator = request.user.groups.filter(name='operator').exists()

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'COMPLETED':
        return HttpResponseForbidden()
    if not (lot.company == profile.company or operator):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            lot.status = 'REVOKED'
            lot.full_clean()
            lot.save()

            event = Event.objects.create(
                type='REVOKED',
                comment=form.data['comment'],
                created_by=request.user
            )
            event.full_clean()
            event.save()

            lot.events.add(event)

            messages.add_message(request, messages.SUCCESS, gettext('Лот аннулирован.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = CommentForm()

    return render(request, 'standard/pages/lot_revoke.html', {'lot': lot, 'form': form})

#EOZ_SENT
@login_required
@permission_required('standard.edit_lot')
def eoz_sent(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)
    operator = request.user.groups.filter(name='operator').exists()

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()

    if not operator:
        return HttpResponseForbidden()

    if lot.eoz_status == 'NOT_SENT' and lot.status != 'DRAFT':
        lot_publish(lot)
        lot.eoz_status = 'PUBLISH_SENT'
        messages.add_message(request, messages.SUCCESS, gettext('Отправлено: Опубликовано'))
    elif lot.eoz_status == 'PUBLISH_SENT' and lot.result:
        lot_result(lot)
        lot.eoz_status = 'RESULT_SENT'
        messages.add_message(request, messages.SUCCESS, gettext('Отправлено: Результат'))
    else:
        return HttpResponseForbidden()

    lot.full_clean()
    lot.save()

    return redirect('lot_detail', uuid=lot.uuid)

