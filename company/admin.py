from django.contrib import admin
from .models import Company


class CompanySettings(admin.ModelAdmin):
    list_display = ('name', 'type', 'status')


admin.site.register(Company, CompanySettings)
