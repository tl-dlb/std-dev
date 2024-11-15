from django.contrib import admin
from .models import Counter


class CounterSettings(admin.ModelAdmin):
    list_display = ('type', 'last_number')


admin.site.register(Counter, CounterSettings)
