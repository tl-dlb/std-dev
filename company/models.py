import random
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy
from clearing.models import Wallet
from . import enums



class Company(models.Model):
    name         = models.CharField(max_length=1024, default='', verbose_name=gettext_lazy('Наименование'))
    idn          = models.CharField(max_length=12,   default='', verbose_name=gettext_lazy('БИН/ИИН'), unique=True, null=True, blank=True)
    type         = models.CharField(max_length=32,   default='', verbose_name=gettext_lazy('Тип'),    choices=enums.COMPANY_TYPE_CHOICES)
    status       = models.CharField(max_length=32,   default='', verbose_name=gettext_lazy('Статус'), choices=enums.COMPANY_STATUS_CHOICES)
    address      = models.CharField(max_length=256,  default='', verbose_name=gettext_lazy('Адрес'))
    email        = models.CharField(max_length=256,  default='', verbose_name=gettext_lazy('E-mail'))
    phone        = models.CharField(max_length=256,  default='', verbose_name=gettext_lazy('Телефоны'))
    bank_details = models.CharField(max_length=1024, default='', verbose_name=gettext_lazy('Банковские реквизиты'))
    exchange_id  = models.IntegerField(unique=True, verbose_name=gettext_lazy('Биржевой идентификатор'), null=True)
    created_by   = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_companies')
    updated_by   = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='updated_companies')
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(default=timezone.now)

    clients = models.ManyToManyField('self', blank=True)

    class Meta:
        verbose_name = gettext_lazy('Компания')
        verbose_name_plural = gettext_lazy('Компании')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.exchange_id:
            self.exchange_id = random.randint(100000, 999999)
        super(Company, self).save(*args, **kwargs)

    @property
    def balance_guarantee(self):
        da_company = Wallet.objects.filter(idn=self.idn).first()
        if da_company is None:
            return None

        return da_company.available_amount

    @property
    def blocked_guarantee(self):
        da_company = Wallet.objects.filter(idn=self.idn).first()
        if da_company is None:
            return None

        return da_company.locked_amount

    @property
    def clearing_code(self):
        da_company = Wallet.objects.filter(idn=self.idn).first()
        if da_company is None:
            return None

        return da_company.account_number
