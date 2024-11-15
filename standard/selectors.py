from datetime import datetime, timedelta, time
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import Lot


# def get_lots(request):
#     company = request.user.profile.company
#     lots = Lot.objects.exclude(status='DELETED').all().order_by('-created_at')
#     lots = lots.exclude(Q(status='DRAFT') & ~Q(company=company))
#
#     if request.GET.get('name'):
#         lots = lots.filter(name__icontains=request.GET.get('name'))
#
#     if request.GET.get('number'):
#         lots = lots.filter(number__icontains=request.GET.get('number'))
#
#     if request.GET.get('sum'):
#         lots = lots.filter(sum__icontains=request.GET.get('sum'))
#
#     if request.GET.get('company'):
#         lots = lots.filter(company__name__icontains=request.GET.get('company'))
#
#     if request.GET.get('client'):
#         lots = lots.filter(client__name__icontains=request.GET.get('client'))
#
#     if request.GET.get('status') and request.GET.get('status') != 'ALL':
#         lots = lots.filter(status=request.GET.get('status'))
#
#     if request.GET.get('eoz_status') and request.GET.get('eoz_status') != 'ALL':
#         lots = lots.filter(eoz_status=request.GET.get('eoz_status')).exclude(status='DRAFT')
#
#     if request.GET.get('sub_bg'):
#         sub_bg = datetime.strptime(request.GET.get('sub_bg'), "%d.%m.%Y").date()
#         lots = lots.filter(submission_begin__gte=sub_bg)
#
#     if request.GET.get('sub_bl'):
#         sub_bl = datetime.strptime(request.GET.get('sub_bl'), "%d.%m.%Y").date()+timedelta(days=1)
#         lots = lots.filter(submission_begin__lte=sub_bl)
#
#     if request.GET.get('sub_eg'):
#         sub_eg = datetime.strptime(request.GET.get('sub_eg'), "%d.%m.%Y").date()
#         lots = lots.filter(submission_end__gte=sub_eg)
#
#     if request.GET.get('sub_el'):
#         sub_el = datetime.strptime(request.GET.get('sub_el'), "%d.%m.%Y").date()+timedelta(days=1)
#         lots = lots.filter(submission_end__lte=sub_el)
#
#     if request.GET.get('bid_bg'):
#         bid_bg = datetime.strptime(request.GET.get('bid_bg'), "%d.%m.%Y").date()
#         lots = lots.filter(bidding_begin__gte=bid_bg)
#
#     if request.GET.get('bid_bl'):
#         bid_bl = datetime.strptime(request.GET.get('bid_bl'), "%d.%m.%Y").date()+timedelta(days=1)
#         lots = lots.filter(bidding_begin__lte=bid_bl)
#
#
#     return lots


def get_lots(request):
    company = request.user.profile.company
    if request.user.groups.filter(name='operator').exists() or request.user.is_staff:
        lots = Lot.objects.all().order_by('-created_at')
    elif request.user.groups.filter(name='observer').exists():
        date_value = timezone.now()
        date_gte = datetime.combine(date_value, time.min)
        date_lte = datetime.combine(date_value, time.max)
        lots = Lot.objects.filter(status='COMPLETED').filter(bidding_end__range=(date_gte, date_lte)).order_by('-created_at')
    else:
        lots = Lot.objects.exclude(status='DELETED').all().order_by('-created_at')
        lots = lots.exclude(Q(status='DRAFT') & ~Q(company=company))

    search_query = request.GET.get('search')
    if search_query:
        lots = lots.filter(
            Q(name__icontains=search_query) |
            Q(number__icontains=search_query) |
            Q(sum__icontains=search_query)
        )
    filter_company = request.GET.get('company')
    if filter_company:
        lots = lots.filter(company__name__icontains=filter_company)

    client = request.GET.get('client')
    if client:
        lots = lots.filter(client__name__icontains=client)

    if request.GET.get('status') and request.GET.get('status') != 'ALL':
        lots = lots.filter(status=request.GET.get('status'))

    if request.GET.get('sub_bg'):
        sub_bg = datetime.strptime(request.GET.get('sub_bg'), "%d.%m.%Y").date()
        lots = lots.filter(submission_begin__gte=sub_bg)

    if request.GET.get('sub_bl'):
        sub_bl = datetime.strptime(request.GET.get('sub_bl'), "%d.%m.%Y").date()+timedelta(days=1)
        lots = lots.filter(submission_begin__lte=sub_bl)

    if request.GET.get('sub_eg'):
        sub_eg = datetime.strptime(request.GET.get('sub_eg'), "%d.%m.%Y").date()
        lots = lots.filter(submission_end__gte=sub_eg)

    if request.GET.get('sub_el'):
        sub_el = datetime.strptime(request.GET.get('sub_el'), "%d.%m.%Y").date()+timedelta(days=1)
        lots = lots.filter(submission_end__lte=sub_el)

    if request.GET.get('bid_bg'):
        bid_bg = datetime.strptime(request.GET.get('bid_bg'), "%d.%m.%Y").date()
        lots = lots.filter(bidding_begin__gte=bid_bg)

    if request.GET.get('bid_bl'):
        bid_bl = datetime.strptime(request.GET.get('bid_bl'), "%d.%m.%Y").date()+timedelta(days=1)
        lots = lots.filter(bidding_begin__lte=bid_bl)
    return lots
