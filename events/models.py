from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Event(models.Model):
    type       = models.CharField(default='', max_length=32)
    comment    = models.CharField(default='', max_length=1024, verbose_name='Комментарий', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='events')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return 'id: %s, type: %s, comment: %s' % (self.id, self.type, self.comment)
