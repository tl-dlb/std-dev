from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import gettext_lazy

from standard.models import Lot, Position, Application, Bid
from company.models import Company
from signature.models import Signature

from standard import enums
from files.enums import FILE_TYPE_CHOICES
from .fields import ClientChoiceField
from company import selectors


#LOT CREATE, EDIT
class LotForm(forms.ModelForm):
    class Meta:
        model   = Lot
        fields  = ('name', 'type', 'client', 'submission_begin', 'submission_end', 'bidding_begin', 'qualification', 'subsoil', 'guarantee', 'guarantee_amount')
        widgets = {
            'name'            : forms.TextInput(),
            'type'            : forms.Select(choices=enums.LOT_TYPE_CHOICES),
            'submission_begin': forms.DateTimeInput(format='%d.%m.%Y %H:%M', attrs={'class':'form-control datetimepicker border-gray-300 border rounded-md bg-white text-left shadow-sm hover:cursor-pointer css-11vi78b-control'}),
            'submission_end'  : forms.DateTimeInput(format='%d.%m.%Y %H:%M', attrs={'class':'form-control datetimepicker border-gray-300 border rounded-md bg-white text-left shadow-sm hover:cursor-pointer css-11vi78b-control'}),
            'bidding_begin'   : forms.DateTimeInput(format='%d.%m.%Y %H:%M', attrs={'class':'form-control datetimepicker border-gray-300 border rounded-md bg-white text-left shadow-sm hover:cursor-pointer css-11vi78b-control'}),
            'guarantee'       : forms.CheckboxInput(attrs={'id':'guarantee-input'}),
            'guarantee_amount': forms.NumberInput(attrs={'id':'guarantee-amount-input'}),
        }
    client = forms.ModelChoiceField(queryset=None, label=gettext_lazy('Заказчик'))
    comment = forms.CharField(label=gettext_lazy('Причина внесения изменений'), max_length=1024)

    def __init__(self, user, *args, **kwargs):
        super(LotForm, self).__init__(*args, **kwargs)
        self.fields['submission_begin'].initial = ''
        self.fields['submission_end'].initial   = ''
        self.fields['bidding_begin'].initial    = ''
        self.fields['client'].queryset = user.profile.company.clients.filter(status='ACTIVE', type='CUSTOMER').all()
        
        if self.instance.status in ('PUBLISHED', 'SUBMISSION'):
            del self.fields['name']
            del self.fields['type']
            del self.fields['client']
            del self.fields['qualification']
            del self.fields['subsoil']
            del self.fields['guarantee']
            del self.fields['guarantee_amount']

        if self.instance.status == 'SUBMISSION':
            del self.fields['submission_begin']

        if self.instance.status == 'DRAFT' or self.instance.id is None:
            del self.fields['comment']

    def clean_submission_begin(self):
        data = self.cleaned_data['submission_begin']
        if data < timezone.now():
            raise ValidationError(gettext_lazy('Начало приема заявок не может быть в прошлом'))
        return data

    def clean_submission_end(self):
        data = self.cleaned_data['submission_end']
        if data < timezone.now():
            raise ValidationError(gettext_lazy('Окончание приема заявок не может быть в прошлом'))
        return data

    def clean_bidding_begin(self):
        data = self.cleaned_data['bidding_begin']
        if data < timezone.now():
            raise ValidationError(gettext_lazy('Начало аукциона не может быть в прошлом'))
        return data

    def clean_guarantee_amount(self):
        guarantee = self.cleaned_data['guarantee']
        guarantee_amount = self.cleaned_data['guarantee_amount']
        if guarantee is True and guarantee_amount == 0:
            raise ValidationError(gettext_lazy('Размер гарантийного обеспечения не может быть равен нулю'))
        return guarantee_amount

    def clean(self):
        cleaned_data = super().clean()
        submission_begin = cleaned_data.get('submission_begin')
        submission_end   = cleaned_data.get('submission_end')
        bidding_begin    = cleaned_data.get('bidding_begin')

        if submission_begin and submission_end:
            if submission_begin >= submission_end:
                text = gettext_lazy('Начало приема заявок не может быть равно или раньше окончания приема заявок')
                raise ValidationError({
                    'submission_end': text,
                })

        if submission_end and bidding_begin:
            if submission_end >= bidding_begin:
                text = gettext_lazy('Окончание приема заявок не может быть равно или раньше начала аукциона')
                raise ValidationError({
                    'submission_end': text,
                })


#POSITION CREATE, EDIT
class PositionForm(forms.ModelForm):
    class Meta:
        model   = Position
        fields  = ('name', 'internal_code', 'external_code', 'unified_code', 'unit', 'quantity', 'sum', 'vat', 'payment_terms', 'delivery_days', 'delivery_terms')
        widgets = {
            'sum'         : forms.TextInput(attrs={'id':'sum-input'}),
            'quantity'      : forms.TextInput(attrs={'id':'quantity-input'}),
            'delivery_terms': forms.Textarea(attrs={'rows':5}),
        }
    vat = forms.BooleanField(label=gettext_lazy('НДС'), required=False)

    def clean_sum(self):
        data = self.cleaned_data['sum']
        if data <= 0:
            raise ValidationError(gettext_lazy('Значение не может быть меньше или равно нулю'))
        return data

    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        if data <= 0:
            raise ValidationError(gettext_lazy('Значение не может быть меньше или равно нулю'))
        return data


#UPLOAD FILE
class UploadFileForm(forms.Form):
    type = forms.CharField(label=gettext_lazy('Тип'),  widget=forms.Select(choices=tuple(BLANK_CHOICE_DASH + list(FILE_TYPE_CHOICES))))
    file = forms.FileField(label=gettext_lazy('Файл'), validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx', 'xls', 'rar', 'zip'])])


#COMMENT CANCEL, REVOKE, REJECT
class CommentForm(forms.Form):
    comment = forms.CharField(label=gettext_lazy('Причина'), max_length=1024)


class ApplicationForm(forms.Form):
    use_client_guarantee = forms.BooleanField(
        label=gettext_lazy('Использовать гарантийное обеспечение клиента'),
        required=False
    ) 
    client = ClientChoiceField(
        label=gettext_lazy('Клиент'),
        widget=forms.Select(attrs={'id':'client-select', 'class':'slim-select'}),
        queryset=None
    )
    file = forms.FileField(
        label=gettext_lazy('Прикрепить архивный файл (необязательно)'),
        validators=[FileExtensionValidator(['rar', 'zip'])],
        required=False
    )

    def __init__(self, user, lot, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.user = user
        self.lot  = lot
        self.fields['client'].queryset = self.user.profile.company.clients.filter(status='ACTIVE', type='PARTICIPANT').all()

    def clean_client(self):
        if self.lot.guarantee:    
            client = self.cleaned_data['client']
            if client.balance_guarantee is None:
                raise ValidationError(gettext_lazy('У клиента отсутствует счет в клиринговом центре.'))

            use_client_guarantee = self.cleaned_data['use_client_guarantee']
            if use_client_guarantee:
                if client.balance_guarantee <= 0:
                    raise ValidationError(gettext_lazy('У клиента отсутствуют средства на счету гарантийного обеспечения.'))
                if client.balance_guarantee < self.lot.guarantee_amount_sum:
                    raise ValidationError(gettext_lazy('У клиента отсутствуют средства для участия на счету гарантийного обеспечения.'))
            return client

    def clean(self):
        if self.lot.guarantee: 
            company = self.user.profile.company
            if company.balance_guarantee is None:
                self.add_error(None, ValidationError(gettext_lazy('У вашей компании отсутствует счет в клиринговом центре.')))
            else:
                use_client_guarantee = self.cleaned_data['use_client_guarantee']
                if not use_client_guarantee:
                    if company.balance_guarantee <= 0:
                        self.add_error(None, ValidationError(gettext_lazy('У вашей компании отсутствуют средства на счету гарантийного обеспечения.')))
                    if company.balance_guarantee < self.lot.guarantee_amount_sum:
                        self.add_error(None, ValidationError(gettext_lazy('У вашей компании отсутствуют средства для участия на счету гарантийного обеспечения.')))
        

class BidForm(forms.Form):
    sum = forms.DecimalField(label='Сумма', widget=forms.TextInput(attrs={'id':'sum-input'}))

    def clean_sum(self):
        data = self.cleaned_data['sum']
        if data == 0:
            raise ValidationError(gettext_lazy('Значение не может быть равно нулю'))
        return data


class SignatureForm(forms.ModelForm):
    class Meta:
        model   = Signature
        fields  = ('data',)
        widgets = {'data': forms.Textarea(attrs={'id':'signedXml'})}
        labels  = {'data': gettext_lazy('Подпись')}


class ReportForm(forms.Form):
    start_date = forms.CharField(label=gettext_lazy('Дата отчета от'), widget=forms.DateTimeInput(format='%d.%m.%Y', attrs={'class':' datepicker'}))
    end_date = forms.CharField(label=gettext_lazy('Дата отчета по '),widget=forms.DateTimeInput(format='%d.%m.%Y', attrs={'class': ' datepicker'}))
