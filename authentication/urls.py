from django.urls import include, path

from . import views

urlpatterns = [
    path('login/', views.UpdateLoginView.as_view(), name='login'),
    path('', include('django.contrib.auth.urls')),
    path('register/',       views.register,  name="auth_register"),
    path('signature/', views.auth_signature, name="auth_signature"),
    path('profile', views.profile, name='profile'),
    path('company/add/', views.add_company, name="company_add"),
]