from django.utils.translation import gettext_lazy

LOT_PLATFORM_CHOICES = (
    ('STANDARD', gettext_lazy('Стандартный аукцион')),
)

COUNTER_TYPE_CHOICES = (
    ('LOT', gettext_lazy('Лот')),
)

LOT_STATUS_CHOICES = (
    ('DRAFT',         gettext_lazy('Черновик')),
    ('PUBLISHED',     gettext_lazy('Опубликован')),
    ('SUBMISSION',    gettext_lazy('Прием заявок')),
    ('ADMISSION',     gettext_lazy('Допуск участников')),
    ('ADMITTED',      gettext_lazy('Участники определены')),
    ('BIDDING',       gettext_lazy('Идут торги')),
    ('SUMMARIZING',   gettext_lazy('Подведение итогов')),
    ('COMPLETED',     gettext_lazy('Завершен')),
    ('NOT_COMPLETED', gettext_lazy('Не состоялся')),
    ('CANCELLED',     gettext_lazy('Отменен')),
    ('REVOKED',       gettext_lazy('Аннулирован')),
    ('DELETED',       gettext_lazy('Удален')),
)

RESULT_LOT_STATUS_CHOICES = (
    ('COMPLETED',     gettext_lazy('Завершен')),
    ('NOT_COMPLETED', gettext_lazy('Не состоялся')),
    ('CANCELLED',     gettext_lazy('Отменен')),
    ('REVOKED',       gettext_lazy('Аннулирован'))
)

LOT_TYPE_CHOICES = (
    ('AUCTION_DOWN', gettext_lazy('На понижение')),
    ('AUCTION_UP',   gettext_lazy('На повышение')),
)

POSTITION_STATUS_CHOICES = (
    ('ACTIVE',  gettext_lazy('Активна')),
    ('DELETED', gettext_lazy('Удалена')),
)

APPLICATION_STATUS_CHOICES = (
    ('PENDING',   gettext_lazy('На рассмотрении')),
    ('WITHDRAWN', gettext_lazy('Отозвана')),
    ('ADMITTED',  gettext_lazy('Допущена')),
    ('REJECTED',  gettext_lazy('Отклонена')),
)

RESULT_STATUS_CHOICES = (
    ('NO_ADMISSION',    gettext_lazy('Не произведен допуск участников')),
    ('NO_APPLICATIONS', gettext_lazy('Заявки на участие не поданы')),
    ('ONE_APPLICATION', gettext_lazy('Допущена только одна заявка на участие')),
    ('NO_BIDS',         gettext_lazy('Ценовые предложения не поданы')),
    ('ONE_BID',         gettext_lazy('Подано только одно ценовое предложение')),
    ('HAS_WINNER',      gettext_lazy('Выявлен победитель')),
    ('CANCELLED',       gettext_lazy('Отменен')),
)

UNIT_CHOICES = (
    ('SET',     gettext_lazy('Комплект, штука')),
    ('UNIT',    gettext_lazy('Единица')),
    ('PIECE',   gettext_lazy('Штука')),
    ('TON',     gettext_lazy('Тонна')),
    ('ORDER',   gettext_lazy('Согласно заявке')),
    ('ONE_BID', gettext_lazy('Литр')),
    ('LITER',   gettext_lazy('Киллограм')),
    ('METER',   gettext_lazy('Метр')),
)

EOZ_STATUS_CHOICES = (
    ('NOT_SENT',     gettext_lazy('Не отправлено')),
    ('PUBLISH_SENT', gettext_lazy('Отправлено: Опубликовано')),
    ('RESULT_SENT',  gettext_lazy('Отправлено: Результат')),
)