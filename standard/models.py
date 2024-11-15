import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy

from company.models import Company
from files.models import File
from events.models import Event
from signature.models import Signature
from . import enums


class Lot(models.Model):
    uuid             = models.UUIDField(default=uuid.uuid4, editable=False)
    platform         = models.CharField(default='STANDARD', max_length=32,   choices=enums.LOT_PLATFORM_CHOICES)
    number           = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Номер'))
    status           = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Статус'),       choices=enums.LOT_STATUS_CHOICES)
    type             = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Тип аукциона'), choices=enums.LOT_TYPE_CHOICES)
    mode             = models.CharField(default='STANDARD', max_length=32)
    subject          = models.CharField(default='STANDARD', max_length=32)
    name             = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Наименование'))
    information      = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Дополнительная информация'), blank=True)
    sum              = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name=gettext_lazy('Сумма'))
    vat              = models.BooleanField(default=False, verbose_name=gettext_lazy('НДС'))
    qualification    = models.BooleanField(default=False, verbose_name=gettext_lazy('ПКО'))
    subsoil          = models.BooleanField(default=False, verbose_name=gettext_lazy('В целях недропользования'))
    guarantee        = models.BooleanField(default=False, verbose_name=gettext_lazy('Гарантийное обеспечение'))
    guarantee_amount = models.DecimalField(default=0, 
                                           max_digits=5, 
                                           decimal_places=2, 
                                           verbose_name=gettext_lazy('Размер гарантийного обеспечения (%)'),
                                           validators=[MinValueValidator(0), MaxValueValidator(100)]) 
    company          = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='company_lots', verbose_name=gettext_lazy('Брокер'))
    client           = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='client_lots',  verbose_name=gettext_lazy('Заказчик'))
    created_by       = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='created_lots')
    updated_by       = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='updated_lots')
    created_at       = models.DateTimeField(default=timezone.now)
    updated_at       = models.DateTimeField(default=timezone.now)
    submission_begin = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Начало приема заявок'))
    submission_end   = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Окончание приема заявок'))
    bidding_begin    = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Начало аукциона'))
    bidding_end      = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Окончание аукциона'))

    eoz_status       = models.CharField(default='NOT_SENT', max_length=32, verbose_name=gettext_lazy('Статус ЕОЗ'), choices=enums.EOZ_STATUS_CHOICES)

    files  = models.ManyToManyField(File, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    
    class Meta:
        verbose_name = gettext_lazy('Лот')
        verbose_name_plural = gettext_lazy('Лоты')

    def __str__(self):
        return self.number

    @property
    def changed_event_comment(self):
        event = self.events.filter(type='CHANGED').order_by('-created_at').first()
        return event.comment if event else None

    @property
    def cancelled_event_comment(self):
        event = self.events.filter(type='CANCELLED').order_by('-created_at').first()
        return event.comment if event else None

    @property
    def revoked_event_comment(self):
        event = self.events.filter(type='REVOKED').order_by('-created_at').first()
        return event.comment if event else None

    @property
    def guarantee_amount_sum(self):
        return round(self.sum * self.guarantee_amount / 100, 2)

    @property
    def economy(self):
        if self.result and self.result.bid:
            return round( (self.sum - self.result.bid.sum) / self.sum * 100 , 2)
        return None

    
class Position(models.Model):
    lot            = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='positions')
    status         = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Статус'), choices=enums.POSTITION_STATUS_CHOICES)
    unit           = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Единица измерения'))
    internal_code  = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Код номенклатуры'), blank=True)
    external_code  = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Код ТНВЭД'),        blank=True)
    unified_code   = models.CharField(default='', max_length=32,   verbose_name=gettext_lazy('Код ЕНС ТРУ'),      blank=True)
    name           = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Наименование'))
    payment_terms  = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Условия оплаты') )
    delivery_terms = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Условия поставки'))
    delivery_days  = models.CharField(default='', max_length=1024, verbose_name=gettext_lazy('Срок поставки'))
    price          = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name=gettext_lazy('Цена за единицу'))
    quantity       = models.DecimalField(default=0, max_digits=32, decimal_places=3, verbose_name=gettext_lazy('Количество'))
    sum            = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name=gettext_lazy('Сумма'))
    created_by     = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_positions')
    updated_by     = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='updated_positions')
    created_at     = models.DateTimeField(default=timezone.now)
    updated_at     = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = gettext_lazy('Позиция')
        verbose_name_plural = gettext_lazy('Позиции')

    def __str__(self):
        return self.name

    @property
    def lot_number(self):
        return self.lot.number
    

class Application(models.Model):
    lot        = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name='applications')
    status     = models.CharField(default='', max_length=32, choices=enums.APPLICATION_STATUS_CHOICES,      verbose_name=gettext_lazy('Статус'))
    company    = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='company_applications', verbose_name=gettext_lazy('Брокер'))
    client     = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='client_applications',  verbose_name=gettext_lazy('Участник'))
    created_by = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='created_applications')
    updated_by = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='updated_applications')
    created_at = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Дата подачи'))
    updated_at = models.DateTimeField(default=timezone.now) 

    files  = models.ManyToManyField(File, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    
    class Meta:
        verbose_name = gettext_lazy('Заявка на участие')
        verbose_name_plural = gettext_lazy('Заявки на участие')

    def __str__(self):
        return 'id: %s, company: %s, client: %s, lot: %s' % (self.id, self.company.name, self.client.name, self.lot.number)

    @property
    def rejected_event_comment(self):
        event = self.events.filter(type='REJECTED').order_by('-created_at').first()
        return event.comment if event else None

    @property
    def lot_number(self):
        return self.lot.number

    @property
    def company_name(self):
        return self.company.name

    @property
    def client_name(self):
        return self.client.name
    

class Bid(models.Model):
    lot         = models.ForeignKey(Lot,         on_delete=models.CASCADE, related_name='bids')
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='bids')
    status      = models.CharField(default='', max_length=32, verbose_name=gettext_lazy('Статус'))
    sum         = models.DecimalField(default=0, max_digits=32, decimal_places=2, verbose_name=gettext_lazy('Цена'))
    broker      = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='company_bids',verbose_name=gettext_lazy('Брокер'))
    participant = models.ForeignKey(Company, on_delete=models.RESTRICT, related_name='client_bids',verbose_name=gettext_lazy('Клиент'))
    created_by  = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='created_bids')
    updated_by  = models.ForeignKey(User,    on_delete=models.RESTRICT, related_name='updated_bids')
    created_at  = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Дата подачи'))
    updated_at  = models.DateTimeField(default=timezone.now, verbose_name=gettext_lazy('Дата изменения'))
    
    class Meta:
        verbose_name = gettext_lazy('Цена')
        verbose_name_plural = gettext_lazy('Цены')

    def __str__(self):
        return 'id: %s, lot: %s, sum: %s' % (self.id, self.lot.number, self.sum)

    @property
    def lot_number(self):
        return self.lot.number


class Result(models.Model):
    lot        = models.OneToOneField(Lot, on_delete=models.CASCADE)
    status     = models.CharField(default='', max_length=32, choices=enums.RESULT_STATUS_CHOICES,verbose_name=gettext_lazy('Статус'))
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_results')
    updated_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='updated_results')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    bid        = models.OneToOneField(Bid,       on_delete=models.CASCADE, blank=True, null=True, related_name='bid')
    signature  = models.OneToOneField(Signature, on_delete=models.CASCADE, blank=True, null=True, related_name='signature')
    
    bids       = models.ManyToManyField(Bid, blank=True)
    signatures = models.ManyToManyField(Signature, blank=True)
     
    class Meta:
        verbose_name = gettext_lazy('Итог')
        verbose_name_plural = gettext_lazy('Итоги')

    def __str__(self):
        return 'id: %s, lot: %s, status: %s' % (self.id, self.lot.number, self.status)

    @property
    def lot_number(self):
        return self.lot.number
