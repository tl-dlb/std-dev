import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Entry(models.Model):
    destination = models.CharField(default='EOZ',     max_length=32)
    type        = models.CharField(default='PUBLISH', max_length=32)
    status      = models.CharField(default='DRAFT',   max_length=32)

    subject_id  = models.CharField(default='',        max_length=36)
    payload     = models.TextField(default='')

    created_by  = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_request_entries')
    updated_by  = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='updated_request_entries')
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запрос'

    def __str__(self):
        return self.name