# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# In-memory waiting queue (use Redis in production)
waiting_users = set()

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.channel_name
        await self.accept()
        await self.find_match()

    async def disconnect(self, close_code):
        waiting_users.discard(self.user_id)

    async def find_match(self):
        if waiting_users:
            partner_id = waiting_users.pop()
            room_name = f"room_{self.user_id}_{partner_id}"

            # Notify both users
            await self.channel_layer.send(partner_id, {
                'type': 'start.chat',
                'room_name': room_name,
            })
            await self.send(json.dumps({'type': 'start.chat', 'room_name': room_name}))
        else:
            waiting_users.add(self.user_id)

    async def start_chat(self, event):
        await self.send(json.dumps({'type': 'start.chat', 'room_name': event['room_name']}))
