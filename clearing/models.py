from django.db import models



class Wallet(models.Model):
    idn = models.CharField(max_length=32,   default='', verbose_name='БИН/ИИН компании', unique=True, null=True, blank=True)
    account_number = models.CharField(max_length=32, verbose_name='Клиринговый счет')
    currency_code = models.CharField(max_length=32, verbose_name='Код валюты')
    deposited_amount = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name='Внесено')
    holding_amount = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name='Заморожено')
    locked_amount = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name='Заблокировано')
    available_amount = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name='Свободно')


class Statement(models.Model):
    id_app = models.UUIDField()
    account_number = models.ForeignKey(Wallet, on_delete=models.RESTRICT, verbose_name='Клиринговый счет')
    type = models.CharField(max_length=32, verbose_name='Тип')
    amount = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name='Сумма')
    is_active = models.BooleanField()
    id_operation = models.UUIDField(unique=True)


