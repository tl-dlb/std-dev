from django.urls import path
from . import consumers


websocket_urlpatterns = [
    # path('ws/bidding/(?P<lot_id>[0-9]+)/$', consumers.BiddingConsumer.as_asgi()),
    path('ws/standard/', consumers.StandardConsumer.as_asgi()),
]
