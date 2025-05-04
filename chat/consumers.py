import json
from uuid import uuid4
from channels.generic.websocket import AsyncWebsocketConsumer

waiting_user = None  # Replace with Redis for production

class MatchmakerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        global waiting_user

        if waiting_user is None:
            waiting_user = self
            self.role = 'offerer'  # First user creates the offer
        else:
            room_name = str(uuid4())
            self.role = 'answerer'

            # Notify both users
            await waiting_user.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
                'role': 'offerer',
            }))
            await self.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
                'role': 'answerer',
            }))
            waiting_user = None  # Reset

    async def disconnect(self, close_code):
        global waiting_user
        if waiting_user == self:
            waiting_user = None


class CallConsumer(AsyncWebsocketConsumer):
    rooms = {}  # room_name: [user1, user2]

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        await self.accept()

        if self.room_name not in self.rooms:
            self.rooms[self.room_name] = [self]
        else:
            self.rooms[self.room_name].append(self)

    async def disconnect(self, close_code):
        if self.room_name in self.rooms:
            self.rooms[self.room_name].remove(self)
            if not self.rooms[self.room_name]:
                del self.rooms[self.room_name]

    async def receive(self, text_data):
        for peer in self.rooms.get(self.room_name, []):
            if peer != self:
                await peer.send(text_data)
