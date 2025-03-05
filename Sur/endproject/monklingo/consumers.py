import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        image = data.get('image', '')
        file = data.get('file', '')
        sender_username = data.get('sender', '')

        sender = await User.objects.get(username=sender_username)
        chatroom = await ChatRoom.objects.get(id=self.room_id)

        # บันทึกข้อมูล
        new_message = await Message.objects.create(
            chatroom=chatroom,
            sender=sender,
            content=message,
            image=image,
            file=file,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username,
                'image': image,
                'file': file,
                'timestamp': new_message.timestamp.strftime("%d/%m/%Y %H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'image': event['image'],
            'file': event['file'],
            'timestamp': event['timestamp'],
        }))
