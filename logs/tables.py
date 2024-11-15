import django_tables2 as tables
from django.utils import timezone
import django_filters
from django import forms
from authentication.models import UserLoginHistory
from standard.enums import APPLICATION_STATUS_CHOICES, RESULT_LOT_STATUS_CHOICES
from standard.models import Application, Result

class UserFilter(django_filters.FilterSet):
    start_login_time = django_filters.DateTimeFilter(
        field_name='login_time',
        label='Вход',
        lookup_expr='gte',
        widget=forms.DateTimeInput(attrs={'placeholder': 'Вход с', 'class':'datepicker hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    end_login_time = django_filters.DateTimeFilter(
        field_name='login_time',
        label='Вход',
        lookup_expr='lte',
        widget=forms.DateTimeInput(attrs={'placeholder': 'Вход по',
                                          'class': 'datepicker hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    user__username = django_filters.CharFilter(
        label='Логин',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Логин', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))


    company__idn = django_filters.CharFilter(
        label='БИН',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'БИН', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    class Meta:
        model = UserLoginHistory
        fields = ['user__username','company__idn','start_login_time', 'end_login_time']



class UserTable(tables.Table):
    login_time = tables.Column(verbose_name='Вход в систему участника торгов', empty_values=())
    logout_time = tables.Column(verbose_name='Выход из системы участника торгов', empty_values=())
    idn = tables.Column(verbose_name='Идентификация участника торгов', accessor='user__username')
    company_idn = tables.Column(verbose_name='Компания (БИН)', accessor='company__idn')
    class Meta:
        model = UserLoginHistory
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('id','idn','company_idn', 'login_time', 'logout_time')
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

    def render_login_time(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'

    def render_logout_time(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'

class AppFilter(django_filters.FilterSet):
    datetime_open_auction = django_filters.DateTimeFilter(
        field_name='lot__bidding_begin',
        label='Дата и время открытия торга',
        lookup_expr='date',
        widget=forms.DateTimeInput(attrs={'placeholder': 'Дата и время открытия торга', 'class':' datepicker hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    number_lot = django_filters.NumberFilter(
        field_name='lot__number',
        label='Номер торга',
        lookup_expr='icontains',
        widget=forms.NumberInput(attrs={'placeholder': 'Номер торга', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    status = django_filters.ChoiceFilter(
        label='Статус',
        choices=APPLICATION_STATUS_CHOICES,
        empty_label='Все',
        widget=forms.Select(attrs={'placeholder': 'Статус', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))


    company__name = django_filters.CharFilter(
        label='Брокер',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Брокер', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))


    client__name = django_filters.CharFilter(
        label='Участник',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Участник', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))


    client__idn = django_filters.CharFilter(
        label='БИН',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'БИН', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    class Meta:
        model = Application
        fields = ['datetime_open_auction', 'number_lot', 'status', 'company__name', 'client__name', 'client__idn']


class AppTable(tables.Table):
    datetime_open_auction =tables.Column(verbose_name='Дата и время открытие торга ', accessor='lot__bidding_begin')
    time_orders = tables.Column(verbose_name='Время выставления заявки', accessor='created_at')
    number_lot = tables.Column(verbose_name='Номер торга', accessor='lot__number')
    quantity_lots = tables.Column(verbose_name='Количество лотов', default=1)
    lot_positions_quantity = tables.Column(verbose_name='Количество актива (объем)', empty_values=())
    lot_positions_price = tables.Column(verbose_name='Цена', empty_values=())
    lot_positions_sum = tables.Column(verbose_name='Сумма', empty_values=())
    type_auction = tables.Column(verbose_name='Способ закупа')
    status = tables.TemplateColumn(template_name='log/columns/app_status.html')
    class Meta:
        model = Application
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
        fields = ('id', 'datetime_open_auction', 'time_orders', 'number_lot', 'lot__name', 'quantity_lots',
                  'lot_positions_quantity', 'lot_positions_price','lot_positions_sum', 'status', 'company', 'client',
                  'client__idn', 'type_auction')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for row in self.rows:
            row.record.quantity_lots = 1
            lot = row.record.lot
            if lot:
                quantity = sum(position.quantity for position in lot.positions.all())
                row.record.lot_positions_quantity = quantity
                price = sum(position.price for position in lot.positions.all())
                row.record.lot_positions_price = price
                position_sum = sum(position.sum for position in lot.positions.all())
                row.record.lot_positions_sum = position_sum
                if lot.subsoil:
                    row.record.type_auction = "В целях недропользования"
                else:
                    row.record.type_auction = "Общий закуп"

    def render_datetime_open_auction(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'


    def render_time_orders(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'

class ResultFilter(django_filters.FilterSet):
    datetime_open_auction = django_filters.DateTimeFilter(
        field_name='lot__bidding_begin',
        label='Начало торга с',
        lookup_expr='gte',
        widget=forms.DateTimeInput(attrs={'placeholder': 'Начало торга с', 'class':'datepicker hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    datetime_close_auction = django_filters.DateTimeFilter(
        field_name='lot__bidding_begin',
        label='Начало торга по',
        lookup_expr='lte',
        widget=forms.DateTimeInput(attrs={'placeholder': 'Начало торга по', 'class':'datepicker hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    lot__number = django_filters.NumberFilter(
        field_name='lot__number',
        label='Номер торга',
        lookup_expr='icontains',
        widget=forms.NumberInput(attrs={'placeholder': 'Номер торга', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    lot__name = django_filters.CharFilter(
        label='Наименование',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Наименование',
                                      'class': 'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))
    lot__status = django_filters.ChoiceFilter(
        label='Статус',
        choices=RESULT_LOT_STATUS_CHOICES,
        empty_label='Все',
        widget=forms.Select(attrs={'placeholder': 'Статус', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    seller_broker_name = django_filters.CharFilter(
        label='Брокер продавца',
        field_name='lot__company__name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Брокер продавца', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    seller_bin = django_filters.CharFilter(
        label='БИН продавца',
        field_name='lot__client__idn',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'БИН продавца',
                                      'class': 'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    buyer_broker_name = django_filters.CharFilter(
        label='Брокер покупателя',
        field_name='bid__broker__name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Брокер покупателя', 'class':'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    buyer_bin = django_filters.CharFilter(
        label='БИН покупателя',
        field_name='bid__participant__idn',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'БИН покупателя',
                                      'class': 'hidden h-full border-0 pt-3 pl-12 text-sm text-gray-900 placeholder-gray-500 focus:border-transparent focus:placeholder-gray-400 focus:outline-none focus:ring-0 sm:block'}))

    class Meta:
        model = Result
        fields = ['datetime_open_auction','datetime_close_auction', 'lot__number', 'lot__name','lot__status',
                  'seller_broker_name', 'seller_bin', 'buyer_broker_name', 'buyer_bin']




class ResultTable(tables.Table):
    datetime_open_auction =tables.Column(verbose_name='Дата и время открытия торга', accessor='lot__bidding_begin')
    datetime_close_auction = tables.Column(verbose_name='Дата и время закрытия торга', accessor='lot__bidding_end')
    datetime_deals = tables.Column(verbose_name='Дата и время совершения сделки', accessor='lot__bidding_end')
    quantity_lots = tables.Column(verbose_name='Количество лотов', default=1)
    lot_positions_quantity = tables.Column(verbose_name='Количество актива (объем)', empty_values=())
    lot_positions_price = tables.Column(verbose_name='Цена', empty_values=())
    lot_positions_sum = tables.Column(verbose_name='Сумма', empty_values=())
    seller_broker_name = tables.Column(verbose_name='Брокер продавца', accessor='lot__company')
    seller_name = tables.Column(verbose_name='Продавец', accessor='lot__client')
    seller_bin = tables.Column(verbose_name='БИН продавца', accessor='lot__client__idn')
    buyer_broker_name = tables.Column(verbose_name='Брокер покупателя', accessor='bid__broker')
    buyer_name = tables.Column(verbose_name='Покупатель', accessor='bid__participant')
    buyer_bin = tables.Column(verbose_name='БИН покупателя', accessor='bid__participant__idn')
    type_auction = tables.Column(verbose_name='Способ закупа')
    lot_result_status = tables.TemplateColumn(template_name="log/columns/result_status.html", verbose_name='Статус лота')
    class Meta:
        model = Result
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
        fields = ('id','datetime_open_auction', 'datetime_close_auction','datetime_deals', 'lot__number', 'lot__name',
                  'lot_result_status', 'quantity_lots', 'lot_positions_quantity', 'lot_positions_price',
                  'lot_positions_sum',  'status', 'seller_broker_name', 'seller_name','seller_bin', 'buyer_broker_name',
                  'buyer_name','buyer_bin', 'type_auction')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for row in self.rows:
            row.record.quantity_lots = 1
            lot = row.record.lot
            if lot:
                quantity = sum(position.quantity for position in lot.positions.all())
                row.record.lot_positions_quantity = quantity
                price = sum(position.price for position in lot.positions.all())
                row.record.lot_positions_price = price
                position_sum = sum(position.sum for position in lot.positions.all())
                row.record.lot_positions_sum = position_sum
                if lot.subsoil:
                    row.record.type_auction = "В целях недропользования"
                else:
                    row.record.type_auction = "Общий закуп"

    def render_datetime_open_auction(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'

    def render_datetime_close_auction(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'

    def render_datetime_deals(self, value):
        return value.astimezone(timezone.get_current_timezone()).strftime('%d.%m.%Y %H:%M:%S.%f')[:-3] if value else '-'