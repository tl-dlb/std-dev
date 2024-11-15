from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from authentication.models import Profile
from notification.models import Notification

@login_required
def detail(request, id):
    notification = Notification.objects.get(pk=id)
    notification.status = 'READ'
    notification.save()
    return render(request, 'notification.html', {'notification': notification})

@login_required
def list(request):
    pass

