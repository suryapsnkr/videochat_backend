# matchmaker/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from uuid import uuid4

waiting_user = None  # Global variable for demo (use Redis for production)

class MatchmakerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        global waiting_user
        if waiting_user is None:
            # First user, wait for match
            waiting_user = self
        else:
            # Match found
            room_name = str(uuid4())
            await waiting_user.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            await self.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            waiting_user = None  # reset

    async def disconnect(self, close_code):
        global waiting_user
        if waiting_user == self:
            waiting_user = None
