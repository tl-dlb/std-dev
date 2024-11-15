from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy

from .models import Company
from .enums import CREATE_COMPANY_TYPE_CHOICES


#COMPANY CREATE, EDIT
class CompanyForm(forms.ModelForm):
    idn = forms.CharField(
        label=gettext_lazy('БИН/Прочее'),
        required=False,
        # validators=[RegexValidator(regex=r'^[0-9]{12,12}$', message='Введите правильный БИН/ИИН')]
    )
    email = forms.EmailField()

    class Meta:
        model   = Company
        fields  = ('name', 'idn', 'type', 'address', 'email', 'phone', 'bank_details')
        widgets = {
            'type'        : forms.Select(),
            'bank_details': forms.Textarea(attrs={'rows':5}),
        }
 
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = CREATE_COMPANY_TYPE_CHOICES
