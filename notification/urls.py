from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *

app_name = 'notification'

urlpatterns = [
    path('notification/<int:id>/', detail, name='notification'),
]