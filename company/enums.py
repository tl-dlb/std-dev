from django.utils.translation import gettext_lazy

COMPANY_STATUS_CHOICES = (
    ('PENDING',  gettext_lazy('На рассмотрении')),
    ('ACTIVE',   gettext_lazy('Активен')),
    ('BLOCKED',  gettext_lazy('Заблокирован')),
    ('DELETED',  gettext_lazy('Удален')),
)

COMPANY_TYPE_CHOICES = (
    ('PARTICIPANT', gettext_lazy('Участник')),
    ('CUSTOMER',    gettext_lazy('Заказчик')),
    ('TRADER',      gettext_lazy('Брокер')),
    ('OPERATOR',    gettext_lazy('Оператор')),
    ('OBSERVER',    gettext_lazy('Наблюдатель')),
)

CREATE_COMPANY_TYPE_CHOICES = (
    ('PARTICIPANT', gettext_lazy('Участник')),
    ('CUSTOMER',    gettext_lazy('Заказчик')),
)
