from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy


class Signature(models.Model):
    type         = models.CharField(max_length=32,    default='REPORT', verbose_name=gettext_lazy('Тип'))
    status       = models.CharField(max_length=32,    default='VALID',  verbose_name=gettext_lazy('Статус'))
    data         = models.CharField(max_length=32768, default='',       verbose_name=gettext_lazy('Данные'))

    created_by   = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_signatures')
    created_at   = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = gettext_lazy('Подпись')
        verbose_name_plural = gettext_lazy('Подписи')

    def __str__(self):
        return 'id: %s, data: %s...' % (self.id, self.data[0:200])