from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models

STATUS_CHOICES = (
    ('READ', 'Прочитано'),
    ('UNREAD', 'Непрочитано'),
)


class Notification(models.Model):
    title = models.CharField(default='', max_length=1024, verbose_name='Тема')
    content = models.CharField(default='', max_length=1024, verbose_name='Содержание')
    status = models.CharField(default='UNREAD', max_length=32, verbose_name='Статус', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    recipient = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name='Получатель')
