from django import forms


class CompanyFilterForm(forms.Form):
    # name   = forms.CharField()
    # idn    = forms.CharField()
    # status = forms.CharField()
    search = forms.CharField()
 