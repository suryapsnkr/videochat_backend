# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

waiting_user = None

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        global waiting_user
        if waiting_user is None:
            # First user waits
            waiting_user = self
            self.partner = None
        else:
            # Second user connects and they are matched
            self.partner = waiting_user
            self.partner.partner = self
            waiting_user = None

            # Notify both with who is offerer
            await self.send(text_data=json.dumps({'type': 'matched', 'offerer': True}))
            await self.partner.send(text_data=json.dumps({'type': 'matched', 'offerer': False}))

    async def disconnect(self, close_code):
        if hasattr(self, 'partner') and self.partner:
            try:
                await self.partner.send(text_data=json.dumps({'type': 'partner_disconnected'}))
                self.partner.partner = None
            except:
                pass
        global waiting_user
        if waiting_user == self:
            waiting_user = None

    async def receive(self, text_data):
        if hasattr(self, 'partner') and self.partner:
            await self.partner.send(text_data=text_data)
