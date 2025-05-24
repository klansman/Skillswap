import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print("Connecting WebSocket...")
            print(f"User: {self.scope['user']}")

        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def receive(self, text_data):
        pass

    async def notify(self, event):
        await self.send(text_data=json.dumps(event["data"]))
        



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.swap_id = self.scope['url_route']['kwargs'] ['swap_id']
        self.room_group_name = f"chat{self.swap_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(self.room_group_name,
                                             {
                'type': 'send_message',
                'message': data['message'],
                'sender': data['sender']
            })
    
    async def send_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender']
        }))

