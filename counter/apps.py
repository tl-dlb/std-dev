from django.apps import AppConfig


class CounterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'counter'
    verbose_name = 'Счетчик'