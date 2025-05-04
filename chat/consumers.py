import json
from channels.generic.websocket import AsyncWebsocketConsumer
from uuid import uuid4

waiting_user = None  # Global variable for matchmaking, use Redis in production

class MatchmakerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        global waiting_user
        if waiting_user is None:
            # First user, wait for a match
            waiting_user = self
        else:
            # Match found, create a unique room
            room_name = str(uuid4())
            await waiting_user.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            await self.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            waiting_user = None  # Reset for next match

    async def disconnect(self, close_code):
        global waiting_user
        if waiting_user == self:
            waiting_user = None

    async def receive(self, text_data):
        data = json.loads(text_data)
        room_name = data.get('room_name')
        if room_name:
            # Send the message to the other user in the room
            await self.channel_layer.send(
                room_name,
                {
                    'type': 'chat_message',
                    'message': data
                }
            )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
