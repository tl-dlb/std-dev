from django.urls import path
from .views import *

urlpatterns = [
    path('log_auth/', log_auth, name='log_auth'),
    path('log_app/', log_app, name='log_app'),
    path('log_result/', log_result, name='log_result'),
    path('download_report/<str:name>', download_report, name='download_report'),
    path('download_result/', download_result, name='download_result'),
]