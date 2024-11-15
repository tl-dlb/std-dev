from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from standard.models import Bid, Lot

@receiver(post_save, sender=Bid)
def bid_create(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('standard', {
            'type':'submit_event',
            'message':'{"event":"bidCreated","lotId":"%s", "lotNumber":"%s", "lotName":"%s","bidPrice":"%s"}' % (str(instance.lot.id),str(instance.lot.number), str(instance.lot.name), str(instance.sum)),
        })

@receiver(post_save, sender=Lot)
def lot_update(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'BIDDING':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('standard', {
                'type':'submit_event',
                'message':'{"event":"biddingStarted","lotId":"%s", "lotName":"%s"}' % (str(instance.id), str(instance.name)),
            })
        elif instance.status == 'SUMMARIZING':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('standard', {
                'type':'submit_event',
                'message':'{"event":"biddingStopped","lotId":"%s", "lotName":"%s"}' % (str(instance.id), str(instance.name))
            })
