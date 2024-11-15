from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy

from authentication.enums import CREATE_COMPANY_TYPE_CHOICES
from company.models import Company


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            'name',
            'type',
            'idn',
            'address',
            'email',
            'phone',
            'bank_details',
        )

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = CREATE_COMPANY_TYPE_CHOICES


class CertificateForm(forms.Form):
    signature = forms.CharField(max_length=32768, label=gettext_lazy('Содержимое подписи'),
                                widget=forms.Textarea(attrs={'id': 'signedXml', 'readonly': True, 'class':'flex-1 min-h-[20rem] text-gray-500 rounded-md my-2'}))
