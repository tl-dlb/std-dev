from django.urls import path
from . import views 

urlpatterns = [
    path('p/<int:id>/', views.PublishPostView.as_view(), name='PPV'),
    path('r/<int:id>/', views.ResultPostView.as_view(),  name='RPV'),
    path('c/<int:id>/', views.CompanyPostView.as_view(), name='CPV'),
]
