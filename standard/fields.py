from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy


class ClientChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        balance_string = '{:,}'.format(obj.balance_guarantee).replace(',', ' ').replace('.', ',')  if obj.balance_guarantee else gettext_lazy('отсутствует')
        bin = gettext_lazy('БИН/ИИН')
        balance = gettext_lazy('Баланс')
        return f'{obj.name}, {bin}: {obj.idn}, {balance}: {balance_string}'
