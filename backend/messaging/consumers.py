import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.room_group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")
        if message_type == "message":
            await self.handle_message(data)
        elif message_type == "read":
            await self.handle_read(data)

    async def handle_message(self, data):
        user = self.scope["user"]
        recipient_id = data.get("recipient_id")
        content = data.get("content")

        message = await self.save_message(user.id, recipient_id, content)

        # 发送给发送者
        await self.send(
            text_data=json.dumps(
                {"type": "message", "message": MessageSerializer(message).data}
            )
        )
        # 发送给接收者
        recipient_group_name = f"user_{recipient_id}"
        await self.channel_layer.group_send(
            recipient_group_name,
            {"type": "chat_message", "message": MessageSerializer(message).data},
        )

    async def handle_read(self, data):
        message_id = data.get("message_id")
        await self.mark_as_read(message_id)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, content):
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
        return Message.objects.create(
            sender=sender, recipient=recipient, content=content
        )

    @database_sync_to_async
    def mark_as_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            if not message.is_read:
                message.is_read = True
                message.save()
            return message
        except Message.DoesNotExist:
            return None
