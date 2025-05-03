# yourapp/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope["url_route"]["kwargs"]["room_name"]
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.room,
            {
                "type": "signal_message",
                "message": text_data,
            }
        )

    async def signal_message(self, event):
        await self.send(text_data=event["message"])
