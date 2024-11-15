from django import forms


class LotFilterForm(forms.Form):
    search     = forms.CharField()
    # number   = forms.CharField()
    # sum      = forms.CharField()
    company  = forms.CharField()
    client   = forms.CharField()
    # status   = forms.CharField()
    # sub_bg   = forms.CharField()  #submission_begin_greater
    # sub_bl   = forms.CharField()  #submission_begin_lower
    # sub_eg   = forms.CharField()  #submission_end_greater
    # sub_el   = forms.CharField()  #submission_end_lower
    # bid_bg   = forms.CharField()  #bidding_begin_greater
    # bid_bl   = forms.CharField()  #bidding_begin_lower
    