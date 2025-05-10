import json
from channels.generic.websocket import AsyncWebsocketConsumer

waiting_users = []  # Global queue for matching

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.channel_layer.group_add(self.user_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_id, self.channel_name)
        if self.user_id in waiting_users:
            waiting_users.remove(self.user_id)

    async def receive(self, text_data):
        data = json.loads(text_data)

        msg_type = data.get("type")

        if msg_type == "join":
            await self.handle_join()
        elif msg_type in ["offer", "answer", "candidate"]:
            await self.forward_signal(data)

    async def handle_join(self):
        if self.user_id in waiting_users:
            return

        if waiting_users:
            peer_id = waiting_users.pop(0)
            await self.channel_layer.group_send(peer_id, {
                'type': 'match',
                'peer_id': self.user_id,
            })
            await self.send(text_data=json.dumps({
                'type': 'match',
                'peer_id': peer_id,
            }))
        else:
            waiting_users.append(self.user_id)

    async def forward_signal(self, data):
        to_user = data.get('to')
        data['from'] = self.user_id
        await self.channel_layer.group_send(to_user, {
            'type': 'signal.message',
            'message': data,
        })

    async def signal_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    async def match(self, event):
        await self.send(text_data=json.dumps({
            'type': 'match',
            'peer_id': event['peer_id'],
        }))
