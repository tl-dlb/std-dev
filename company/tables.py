import django_tables2 as tables
from django.utils.translation import gettext_lazy
from django_tables2.utils import A


class ClientTable(tables.Table):
    class Meta:
        template_name = 'django_tables2/bootstrap4.html'
        attrs = {
            'class': 'min-w-full divide-y divide-gray-900',
            'thead': {'class': 'border-b'},
            'tbody': {'class': 'divide-y divide-gray-200'},
            'th': {'class': 'py-3 px-3 text-left text-sm font-semibold text-gray-900'},
            'td': {'class': 'whitespace-nowrap py-4 px-3 text-sm text-gray-900'}
        }
        row_attrs = {
            'class': 'hover:bg-gray-100',
        }
        empty_text = gettext_lazy('Клиенты не найдены')

    name   = tables.LinkColumn(viewname='client_detail', args=[A('id')], attrs={'a': {'style': 'font-weight: medium;'},'th': {'style': 'width: 25%; text-align: start;'}})
    idn    = tables.Column(attrs={'th':{'style':'width: 15%; text-align: start;'}})
    status = tables.Column(attrs={'th':{'style':'width: 10%; text-align: start;'}})
    type   = tables.Column(attrs={'th':{'style':'width: 10%; text-align: start;'}})
    balance_guarantee = tables.TemplateColumn(
        verbose_name=gettext_lazy('Свободное ГО'),
        attrs={'th': {'style': 'width: 20%; text-align: start;'}},
        orderable=False,
        template_name='company/columns/balance_guarantee.html', 
    )
    blocked_guarantee = tables.TemplateColumn(
        verbose_name=gettext_lazy('Заблокированное ГО'),
        attrs={'th': {'style': 'width: 25%; text-align: start;'}},
        orderable=False,
        template_name='company/columns/blocked_guarantee.html', 
    )
    actions = tables.TemplateColumn(attrs={'th': {'style': 'width: 15%; text-align: start;'}}, orderable=False,
                                    template_name='company/columns/company_actions.html',
                                    verbose_name=gettext_lazy('Действия'))


class TraderTable(tables.Table):
    class Meta:
        template_name = 'django_tables2/bootstrap4.html'
        attrs = {'class':'table'}
        empty_text = gettext_lazy('Брокеры не найдены')

    name   = tables.Column(attrs={'th': {'style': 'width: 25%;'}}, orderable=False)
    idn    = tables.Column(attrs={'th': {'style': 'width: 25%;'}}, orderable=False)
    status = tables.Column(attrs={'th': {'style': 'width: 25%;'}}, orderable=False)
    type   = tables.Column(attrs={'th': {'style': 'width: 25%;'}}, orderable=False)