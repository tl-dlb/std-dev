from django.db.models import Q
from .models import Company


def get_initiators():
    return Company.objects.filter(type='INITIATOR').all()

def get_participants():
    return Company.objects.filter(type='PARTICIPANT').all()

def get_clients(request):
    if request.user.groups.filter(name='operator').exists():
        clients = Company.objects.exclude(status='DELETED').all()
    else:
        clients = request.user.profile.company.clients.exclude(status='DELETED').all()
    clients = clients.order_by('-created_at')
    # if request.GET.get('name'):
    #     clients = clients.filter(name__icontains=request.GET.get('name'))
    #
    # if request.GET.get('idn'):
    #     clients = clients.filter(idn__icontains=request.GET.get('idn'))
    # return clients

    search_query = request.GET.get('search')
    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) |
            Q(idn__icontains=search_query) |
            Q(status=search_query)
        )
    if request.GET.get('status') and request.GET.get('status') != 'ALL':
        clients = clients.filter(status=request.GET.get('status'))
    return clients
    