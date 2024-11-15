from decimal import Decimal
import requests
from django.http import HttpResponseForbidden, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import gettext

from authentication.helpers import get_profile_or_403
from config.settings import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY
from standard.models import Bid, Lot
from ..forms import BidForm
from .. import services


#LIST
@login_required
@permission_required('standard.view_bid')
def list(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    is_operator = request.user.groups.filter(name='operator').exists()

    if request.user.groups.filter(name='security').exists():
        raise Http404()

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status not in ('BIDDING', 'SUMMARIZING', 'COMPLETED', 'NOT_COMPLETED'):
        return redirect('lot_detail', uuid=lot.uuid)
    

    visible = lot.company == profile.company or is_operator

    form = BidForm()
    user_app = lot.applications.filter(status='ADMITTED', company=profile.company).first()
    return render(request, 'standard/pages/bid_list.html', {
        'lot'      : lot, 
        'form'     : form,
        'user_app' : user_app,
        'visible'  : visible
        # 'public_key': RECAPTCHA_PUBLIC_KEY
    })


#CREATE
@login_required
@permission_required('standard.add_bid')
def create(request, uuid):
    profile = get_profile_or_403(request=request)
    lot = get_object_or_404(Lot, uuid=uuid)

    if lot.platform != 'STANDARD':
        return HttpResponseForbidden()
    if lot.status != 'BIDDING':
        return redirect('lot_detail', uuid=lot.uuid)

    user_app = lot.applications.filter(status='ADMITTED', company=profile.company).first()

    if not user_app:
        return HttpResponseForbidden()

    # captcha_response = request.POST.get('g-recaptcha-response')
    # if captcha_response:
    #     data = {
    #         'secret': RECAPTCHA_PRIVATE_KEY,
    #         'response': captcha_response,
    #     }
    #     verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    #     verify_result = verify_response.json()
    #     if not verify_result.get('success', False):
    #         messages.add_message(request, messages.WARNING, gettext('Ошибка CAPTCHA. Пожалуйста, повторите попытку.'))
    #         return redirect('lot_bid_list', uuid=lot.uuid)
    # else:
    #     messages.add_message(request, messages.WARNING, gettext('Ошибка CAPTCHA. Пожалуйста, повторите попытку.'))
    #     return redirect('lot_bid_list', uuid=lot.uuid)


    sum_str = request.POST.get('sum', None)
    if sum_str is None:
        messages.add_message(request, messages.WARNING, gettext('Сумма не может быть пустой'))
        return redirect('lot_bid_list', uuid=lot.uuid)

    sum = Decimal(request.POST['sum']).quantize(Decimal(10) ** -2)
    user_bids = lot.bids.filter(application__company=profile.company).all()

    if user_bids.filter(sum=sum).exists():
        messages.add_message(request, messages.WARNING, gettext('От вашей компании уже подано такое ценовое предложение.'))
        return redirect('lot_bid_list', uuid=lot.uuid)

    if lot.type == 'AUCTION_DOWN':
        if sum > lot.sum:
            messages.add_message(request, messages.WARNING, gettext('Ценовое предложение не может быть больше стартовой суммы торга.'))
            return redirect('lot_bid_list', uuid=lot.uuid)
        
        user_min_bid = user_bids.order_by('sum').first()
        if user_min_bid and sum > user_min_bid.sum:
            messages.add_message(request, messages.WARNING, gettext('Ценовое предложение не может быть больше ранее поданного ценового предложения.'))
            return redirect('lot_bid_list', uuid=lot.uuid)

    elif lot.type == 'AUCTION_UP':
        if sum < lot.sum:
            messages.add_message(request, messages.WARNING, gettext('Ценовое предложение не может быть меньше стартовой суммы торга.'))
            return redirect('lot_bid_list', uuid=lot.uuid)

        user_max_bid = user_bids.order_by('sum').last()
        if user_max_bid and sum < user_max_bid.sum:
            messages.add_message(request, messages.WARNING, gettext('Ценовое предложение не может быть меньше ранее поданного ценового предложения.'))
            return redirect('lot_bid_list', uuid=lot.uuid)

    form = BidForm(request.POST)
    if form.is_valid():
        bid = Bid.objects.create(
            lot=lot,
            application=user_app,
            status='ACTIVE',
            sum=sum,
            broker=user_app.company,
            participant=user_app.client,
            created_by=request.user,
            updated_by=request.user,
        )
        bid.full_clean()
        bid.save()

        if lot.type == 'AUCTION_DOWN':
            best_bid = lot.bids.order_by('sum').first()
        elif lot.type == 'AUCTION_UP':
            best_bid = lot.bids.order_by('-sum').first()
        last_bid = lot.bids.order_by('-created_at').first()


        bidding_period = (lot.bidding_end - lot.bidding_begin).seconds//60
        bid_created_delta = (lot.bidding_end - bid.created_at).seconds//60
        if last_bid.sum == best_bid.sum and bid_created_delta < 3 and bidding_period in (15,20,25):
            services.update_bidding_end(lot=lot)

    else:
        for field in form.errors:
            messages.add_message(request, messages.WARNING, form.errors[field].as_text())
    return redirect('lot_bid_list', uuid=lot.uuid)

