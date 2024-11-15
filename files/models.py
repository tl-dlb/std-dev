from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from . import helpers
from . import enums


class File(models.Model):
    field      = models.FileField(blank=False, null=False, upload_to=helpers.get_file_path)
    name       = models.CharField(blank=False, null=False, max_length=1024)
    type       = models.CharField(default='OTHER', max_length=32, choices=enums.FILE_TYPE_CHOICES)
    status     = models.CharField(default='ACTIVE', max_length=32)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_files')
    updated_by = models.IntegerField(default=1)
    #updated_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='updated_files')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'id: %s, name: %s, type: %s' % (self.id, self.name, self.type)
