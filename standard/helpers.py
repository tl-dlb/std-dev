import os
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied


def fetch_pdf_resources(uri, rel):
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT,  uri.replace(settings.MEDIA_URL,  ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path


def get_profile_or_403(request):
    try:
        return request.user.profile
    except ObjectDoesNotExist: 
        raise PermissionDenied('User does not have profile.')