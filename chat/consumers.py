import json
from channels.generic.websocket import AsyncWebsocketConsumer
from uuid import uuid4

# Global variable to simulate matchmaker
waiting_user = None

class MatchmakerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

        global waiting_user
        if waiting_user is None:
            # If no other user is waiting, the current user waits for a match
            waiting_user = self
        else:
            # A match is found, so send the room name to both users
            room_name = str(uuid4())  # Generate a unique room ID for the match
            await waiting_user.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            await self.send(text_data=json.dumps({
                'type': 'start.chat',
                'room_name': room_name,
            }))
            # Reset waiting user after match
            waiting_user = None  

    async def disconnect(self, close_code):
        global waiting_user
        if waiting_user == self:
            waiting_user = None  # Reset when a user disconnects


class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = room_name

        # Add this connection to the room group
        self.group_name = f'call_{self.room_name}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the connection from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the incoming message
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'offer' or message_type == 'answer' or message_type == 'candidate':
            # Send the received message to the other user in the same room
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'webrtc_message',
                    'message': text_data,
                }
            )

    # Handle WebRTC signaling messages (offer, answer, ICE candidate)
    async def webrtc_message(self, event):
        message = event['message']
        await self.send(text_data=message)
