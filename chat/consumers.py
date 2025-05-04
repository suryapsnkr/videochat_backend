# --- Django Backend (Channels + WebRTC Signaling) ---

# matchmaker/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from uuid import uuid4

waiting_user = None

class MatchmakerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        global waiting_user
        if waiting_user is None:
            waiting_user = self
        else:
            room_name = str(uuid4())
            await waiting_user.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
                'is_offerer': True
            }))
            await self.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
                'is_offerer': False
            }))
            waiting_user = None

    async def disconnect(self, close_code):
        global waiting_user
        if waiting_user == self:
            waiting_user = None


# matchmaker/call_consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'signal_message',
                'message': data,
            }
        )

    async def signal_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
