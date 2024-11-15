from django.urls import path

from .views import download

urlpatterns = [
    path('<int:id>/download/', download, name='file_download'),
]