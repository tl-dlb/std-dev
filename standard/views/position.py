from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext

from authentication.helpers import get_profile_or_403
from standard.models import Lot, Position
from ..forms import PositionForm
from .. import selectors
from .. import services

TWO_PLACES = Decimal(10) ** -2
FIVE_PLACES = Decimal(10) ** -5


#POSITION CREATE
@login_required
@permission_required('standard.add_position')
def create(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'DRAFT':
        return HttpResponseForbidden()
    if lot.status == 'DRAFT' and lot.company != profile.company:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            sum    = Decimal(form.data['sum']).quantize(TWO_PLACES)
            quantity = Decimal(form.data['quantity']).quantize(TWO_PLACES)
            position = Position.objects.create(
                lot=lot,
                status='ACTIVE',
                unit=form.data['unit'],
                name=form.data['name'],
                internal_code=form.data['internal_code'],
                external_code=form.data['external_code'],
                unified_code=form.data['unified_code'],
                payment_terms=form.data['payment_terms'],
                delivery_terms=form.data['delivery_terms'],
                delivery_days=form.data['delivery_days'],
                price=Decimal(sum / quantity).quantize(TWO_PLACES),
                quantity=quantity,
                sum=sum,
                created_by=request.user,
                updated_by=request.user,
            )
            position.full_clean()
            position.save()

            services.calc_lot_sum(lot=lot)
            lot.vat = True if request.POST.get('vat') else False
            lot.full_clean()
            lot.save()

            messages.add_message(request, messages.SUCCESS, gettext('Позиция создана.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = PositionForm(initial={'name':lot.name, 'unit':'комплект', 'vat':False})
    return render(request, 'standard/pages/position_create.html', {'lot': lot, 'form': form})


#POSITION EDIT
@login_required
@permission_required('standard.change_position')
def edit(request, uuid, pos_id):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'DRAFT':
        return HttpResponseForbidden()
    if lot.status == 'DRAFT' and lot.company != profile.company:
        return HttpResponseForbidden()

    position = get_object_or_404(Position, pk=pos_id)
    if request.POST:
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save(commit=False)
            position.updated_by = request.user
            position.updated_at = timezone.now()
            position.full_clean()
            position.save()

            services.calc_position_sum(position=position)
            services.calc_lot_sum(lot=lot)

            lot.vat = True if request.POST.get('vat') else False
            lot.full_clean()
            lot.save()

            messages.add_message(request, messages.SUCCESS, gettext('Изменения сохранены.'))
            return redirect('lot_detail', uuid=lot.uuid)
    else:
        form = PositionForm(instance=position, initial={'vat':lot.vat})
    return render(request, 'standard/pages/position_edit.html', {'lot':lot, 'position':position, 'form':form})

