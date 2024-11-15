from django.db import models
from . import enums


class Counter(models.Model):
    type        = models.CharField(default='', max_length=32, choices=enums.COUNTER_TYPE_CHOICES, verbose_name='Тип счетчика') 
    last_number = models.IntegerField(default=0, verbose_name='Последнее значение')

    class Meta:
        verbose_name = 'Счетчик'
        verbose_name_plural = 'Счетчики'

    def __str__(self):
        return self.type
