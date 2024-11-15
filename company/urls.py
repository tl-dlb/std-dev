from django.urls import path
from . import views

urlpatterns = [
    path('client/',                views.list,    name='client_list'),
    path('client/create/',         views.create,  name='client_create'),
    path('client/<int:id>/',       views.detail,  name='client_detail'),
    path('client/<int:id>/edit/',  views.edit,    name='client_edit'),
    path('client/<int:id>/admit/', views.admit,   name='client_admit'),
    path('client/<int:id>/block/', views.block,   name='client_block'),
    path('profile/',               views.profile, name='company_profile'),
]