import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BiddingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lot_id = self.scope['url_route']['kwargs']['lot_id']
        self.bidding_group_name = 'bidding_%s' % self.lot_id

        # Join bidding group
        await self.channel_layer.group_add(
            self.bidding_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave bidding group
        await self.channel_layer.group_discard(
            self.bidding_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json['event']

        # Send submitted event to bidding group
        await self.channel_layer.group_send(
            self.bidding_group_name,
            {
                'type': 'submit_event',
                'event': event
            }
        )

    # Receive event from bidding group
    async def submit_event(self, event):
        event = event['event']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'event': event}))


class StandardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'standard'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(self.group_name, {
            'type':'submit_event',
            'message':message,
        })

    async def submit_event(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message':message}))