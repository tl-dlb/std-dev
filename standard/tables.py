import django_tables2 as tables
from django.utils.translation import gettext_lazy


class LotTable(tables.Table):
    name             = tables.TemplateColumn(attrs={'th':{'style':'width:18%;'}}, template_name='standard/columns/lot_name.html')
    number           = tables.TemplateColumn(attrs={'th':{'style':'width:10%;'}}, template_name='standard/columns/lot_number.html')
    sum              = tables.TemplateColumn(attrs={'th':{'style':'width:10%;'}}, template_name='standard/columns/lot_sum.html')
    submission_begin = tables.DateTimeColumn(attrs={'th':{'style':'width:10%;'}})
    submission_end   = tables.DateTimeColumn(attrs={'th':{'style':'width:10%;'}})
    bidding_begin    = tables.DateTimeColumn(attrs={'th':{'style':'width:10%;'}})
    company          = tables.Column(attrs={'th':{'style':'width:10%;'}})
    client           = tables.Column(attrs={'th':{'style':'width:10%;'}})
    status           = tables.TemplateColumn(attrs={'th':{'style':'width:12%;'}}, template_name='standard/columns/lot_status.html')

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
        empty_text = gettext_lazy('Лоты не найдены')


class ApplicationTable(tables.Table):
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
        empty_text = gettext_lazy('Заявки на участие не поданы')
  
    company    = tables.Column(attrs={'th': {'style': 'width: 20%;'}},         orderable=False)
    client     = tables.TemplateColumn(attrs={'th': {'style': 'width: 20%;'}}, orderable=False, template_name='standard/columns/app_client.html')
    created_at = tables.Column(attrs={'th': {'style': 'width: 15%;'}},         orderable=False)
    file       = tables.TemplateColumn(attrs={'th': {'style': 'width: 15%;'}}, orderable=False, template_name='standard/columns/app_file.html', verbose_name=gettext_lazy('Приложение'))
    status     = tables.TemplateColumn(attrs={'th': {'style': 'width: 15%;'}}, orderable=False, template_name='standard/columns/app_status.html')
    actions    = tables.TemplateColumn(attrs={'th': {'style': 'width: 15%;'}}, orderable=False, template_name='standard/columns/app_actions.html', verbose_name=gettext_lazy('Действия'))
