from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asyncio import Queue

waiting_users = Queue()

class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.partner = None
        await self.send(text_data=json.dumps({"type": "status", "message": "connecting..."}))

        if waiting_users.empty():
            await waiting_users.put(self)
        else:
            partner = await waiting_users.get()
            self.partner = partner
            partner.partner = self
            await self.send(json.dumps({"type": "matched"}))
            await partner.send(json.dumps({"type": "matched"}))

    async def disconnect(self, close_code):
        if self.partner:
            await self.partner.send(json.dumps({"type": "partner_disconnected"}))
            self.partner.partner = None
        else:
            try:
                waiting_users._queue.remove(self)
            except ValueError:
                pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        if self.partner:
            await self.partner.send(text_data)
