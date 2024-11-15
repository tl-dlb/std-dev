from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext

from authentication.helpers import get_profile_or_403
from standard.models import Lot, Result
from .. import services


#CREATE
@login_required
@permission_required('standard.add_result')
def create(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'SUMMARIZING':
        return HttpResponseForbidden()
    if lot.status == 'SUMMARIZING' and not request.user.groups.filter(name='operator').exists():
        return HttpResponseForbidden()

    messages.add_message(request, messages.SUCCESS, gettext('Итоги сформированы'))
    user = request.user

    if not lot.applications.exclude(status='WITHDRAWN').exists():
        services.create_result(lot=lot, status='NO_APPLICATIONS', user=user)
        return redirect('lot_detail', uuid=lot.uuid)

    if lot.applications.filter(status='SUBMITTED').exists():
        services.create_result(lot=lot, status='NO_ADMISSION', user=user)
        return redirect('lot_detail', uuid=lot.uuid)
    
    if lot.applications.filter(status='ADMITTED').count() == 1:
        services.create_result(lot=lot, status='ONE_APPLICATION', user=user)
        return redirect('lot_detail', uuid=lot.uuid)

    if not lot.bids.filter(status='ACTIVE').exists():
        services.create_result(lot=lot, status='NO_BIDS', user=user)
        return redirect('lot_detail', uuid=lot.uuid)

    if lot.bids.filter(status='ACTIVE').count() == 1:
        services.create_result(lot=lot, status='ONE_BID', user=user)
        return redirect('lot_detail', uuid=lot.uuid)

    if lot.type == 'AUCTION_DOWN':
        best_bid = lot.bids.filter(status='ACTIVE').order_by('sum', 'created_at').first()
    if lot.type == 'AUCTION_UP':
        best_bid = lot.bids.filter(status='ACTIVE').order_by('-sum', 'created_at').first()

    result = Result.objects.create(
        lot=lot,
        status='HAS_WINNER',
        created_by=user,
        updated_by=user,
        bid=best_bid,
    )
    result.full_clean()
    result.save()

    return redirect('lot_detail', uuid=lot.uuid)
