from django.contrib import admin
from .models import Lot, Position, Application, Bid, Result


class LotSetting(admin.ModelAdmin):
    list_display  = ('number', 'name', 'sum', 'status',)
    search_fields = ('number', 'name', 'sum',)
    list_filter   = ('status',)

class PositionSetting(admin.ModelAdmin):
    list_display  = ('lot_number', 'sum', 'status',)
    search_fields = ('lot__number', 'sum',)
    list_filter   = ('status',)

class ApplicationSetting(admin.ModelAdmin):
    list_display  = ('lot_number', 'company_name', 'client_name', 'status',)
    search_fields = ('lot__number', 'company__name', 'client__name',)
    list_filter   = ('status',)

class BidSetting(admin.ModelAdmin):
    list_display  = ('lot_number', 'sum', 'status',)
    search_fields = ('lot__number', 'sum',)
    list_filter   = ('status',)

class ResultSetting(admin.ModelAdmin):
    list_display  = ('lot_number', 'status',)
    search_fields = ('lot__number',)
    list_filter   = ('status',)


admin.site.register(Lot, LotSetting)
admin.site.register(Position, PositionSetting)
admin.site.register(Application, ApplicationSetting)
admin.site.register(Bid, BidSetting)
admin.site.register(Result, ResultSetting)
