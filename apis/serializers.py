from rest_framework import serializers
from django.db.models import Q
from standard.models import Lot


class LotListSerializer(serializers.ModelSerializer): 
    type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    changed_event_comment = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    payment_terms = serializers.SerializerMethodField()
    delivery_terms = serializers.SerializerMethodField()
    delivery_days = serializers.SerializerMethodField()
    local_content = serializers.SerializerMethodField()
    customer_contacts = serializers.SerializerMethodField()
    apps_count = serializers.SerializerMethodField()
    rejected_apps_count = serializers.SerializerMethodField()
    accepted_apps = serializers.SerializerMethodField()
    rejected_apps = serializers.SerializerMethodField()
    winner = serializers.SerializerMethodField()
    winner_offer = serializers.SerializerMethodField()
    winner_client_exchange_id = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    def get_type(self, obj):
        return obj.get_type_display()
    def get_status(self, obj):
        return obj.get_status_display()
    def get_changed_event_comment(self, obj):
        return obj.changed_event_comment if obj.changed_event_comment else 'нет'
    def get_customer_name(self, obj):
        return obj.client.name
    def get_customer_details(self, obj):
        return '%s %s' % (obj.client.address, obj.client.bank_details)
    def get_quantity(self, obj):
        return obj.positions.filter(status='ACTIVE').first().quantity
    def get_unit(self, obj):
        return obj.positions.filter(status='ACTIVE').first().unit
    def get_payment_terms(self, obj):
        return obj.positions.filter(status='ACTIVE').first().payment_terms
    def get_delivery_terms(self, obj):
        return obj.positions.filter(status='ACTIVE').first().delivery_terms
    def get_delivery_days(self, obj):
        return obj.positions.filter(status='ACTIVE').first().delivery_days
    def get_local_content(self, obj):
        return 'нет'
    def get_customer_contacts(self, obj):
        return obj.client.email
    def get_apps_count(self, obj):
        return obj.applications.filter(Q(status='ADMITTED') | Q(status='REJECTED')).count()
    def get_rejected_apps_count(self, obj):
        return obj.applications.filter(status='REJECTED').count()
    def get_rejected_apps(self, obj):
        apps = obj.applications.filter(status='REJECTED').all()
        json = []
        for app in apps:
            json.append({'company':app.company.name, 'client':app.client.name, 'client_exchange_id':app.client.exchange_id})
        return json
    def get_accepted_apps(self, obj):
        apps = obj.applications.filter(status='ADMITTED').all()
        json = []
        for app in apps:
            json.append({'company':app.company.name, 'client':app.client.name, 'client_exchange_id':app.client.exchange_id})
        return json
    def get_winner(self, obj):
        if obj.status == 'COMPLETED':
            return obj.result.bid.application.company.name
        else:
            return ''
    def get_winner_offer(self, obj):
        if obj.status == 'COMPLETED':
            return obj.result.bid.sum
        else:
            return ''
    def get_winner_client_exchange_id(self, obj):
        if obj.status == 'COMPLETED':
            return obj.result.bid.application.client.exchange_id
        else:
            return ''
    def get_documents(self, obj):
        return '<a href="https://std.webmts.net/api/lot/%s/files/download/">Скачать</a>' % (obj.id)
    

    class Meta:
        model = Lot
        fields = ('id', 
                'number', 
                'type', 
                'status', 
                'changed_event_comment', 
                'name', 
                'customer_name',
                'customer_details',
                'sum',
                'quantity',
                'unit',
                'payment_terms',
                'delivery_terms',
                'delivery_days',
                'local_content',  
                'customer_contacts',
                'submission_end',
                'bidding_begin',
                'documents',
                'apps_count',
                'rejected_apps_count',
                'rejected_apps',
                'accepted_apps',
                'winner',
                'winner_offer',
                'winner_client_exchange_id'
                )