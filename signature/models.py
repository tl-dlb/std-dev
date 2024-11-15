from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Signature(models.Model):
    type         = models.CharField(max_length=32,    default='')
    status       = models.CharField(max_length=32,    default='')  
    data         = models.CharField(max_length=32768, default='', verbose_name='Содержимое подписи')
    value        = models.CharField(max_length=1024,  default='--')
    certificate  = models.CharField(max_length=32768, default='--')
    name         = models.CharField(max_length=1024,  default='')
    company      = models.CharField(max_length=1024, default='')
    bin          = models.CharField(max_length=1024, default='')
    created_by   = models.ForeignKey(User, on_delete=models.RESTRICT,   related_name='signatures')
    created_at   = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Подпись'
        verbose_name_plural = 'Подписи'

    def __str__(self):
        return 'id: %s, data: %s...' % (self.id, self.data[0:200])