import os
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from files.models import File


@login_required
def download(request, id):
    file = get_object_or_404(File, pk=id)
    path = os.path.join(settings.MEDIA_ROOT, file.field.path)
    if os.path.exists(path):
        return FileResponse(open(path, 'rb'), filename=file.name) 