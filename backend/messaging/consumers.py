import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, GroupMessage, GroupChat
from .serializers import MessageSerializer, GroupMessageSerializer

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            # 私聊房间
            self.private_room_name = f"user_{user.id}"
            await self.channel_layer.group_add(
                self.private_room_name, self.channel_name
            )

            # 加入所有群聊房间
            group_chats = await self.get_user_group_chats(user.id)
            for group_id in group_chats:
                room_name = f"group_{group_id}"
                await self.channel_layer.group_add(room_name, self.channel_name)

            await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if not user.is_anonymous:
            # 离开私聊房间
            await self.channel_layer.group_discard(
                self.private_room_name, self.channel_name
            )

            # 离开所有群聊房间
            group_chats = await self.get_user_group_chats(user.id)
            for group_id in group_chats:
                room_name = f"group_{group_id}"
                await self.channel_layer.group_discard(room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "private_message":
            await self.handle_private_message(data)
        elif message_type == "group_message":
            await self.handle_group_message(data)
        elif message_type == "read":
            await self.handle_read(data)
        elif message_type == "join_group":
            await self.handle_join_group(data)

    async def handle_private_message(self, data):
        """处理私聊消息"""
        user = self.scope["user"]
        recipient_id = data.get("recipient_id")
        content = data.get("content")

        message = await self.save_private_message(user.id, recipient_id, content)

        # 发送给发送者
        await self.send(
            text_data=json.dumps(
                {"type": "private_message", "message": MessageSerializer(message).data}
            )
        )
        # 发送给接收者
        recipient_group_name = f"user_{recipient_id}"
        await self.channel_layer.group_send(
            recipient_group_name,
            {"type": "chat_message", "message": MessageSerializer(message).data},
        )

    async def handle_group_message(self, data):
        """处理群聊消息"""
        user = self.scope["user"]
        group_id = data.get("group_id")
        content = data.get("content")

        # 检查用户是否是群成员
        is_member = await self.check_group_membership(user.id, group_id)
        if not is_member:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "您不是该群的成员"})
            )
            return

        message = await self.save_group_message(user.id, group_id, content)

        # 发送给所有群成员（除了发送者）
        group_room_name = f"group_{group_id}"
        await self.channel_layer.group_send(
            group_room_name,
            {
                "type": "group_chat_message",
                "message": GroupMessageSerializer(message).data,
            },
        )

    async def handle_read(self, data):
        """处理消息已读"""
        message_id = data.get("message_id")
        await self.mark_as_read(message_id)

    async def handle_join_group(self, data):
        """处理用户加入群聊房间"""
        user = self.scope["user"]
        group_id = data.get("group_id")

        # 检查用户是否是群成员
        is_member = await self.check_group_membership(user.id, group_id)
        if not is_member:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "您不是该群的成员"})
            )
            return

        # 加入群聊房间
        room_name = f"group_{group_id}"
        await self.channel_layer.group_add(room_name, self.channel_name)
        await self.send(
            text_data=json.dumps({"type": "group_joined", "group_id": group_id})
        )

    async def chat_message(self, event):
        """发送私聊消息给客户端"""
        await self.send(text_data=json.dumps(event))

    async def group_chat_message(self, event):
        """发送群聊消息给客户端"""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_private_message(self, sender_id, recipient_id, content):
        """保存私聊消息"""
        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)
        return Message.objects.create(
            sender=sender, recipient=recipient, content=content
        )

    @database_sync_to_async
    def save_group_message(self, sender_id, group_id, content):
        """保存群聊消息"""
        sender = User.objects.get(id=sender_id)
        group = GroupChat.objects.get(id=group_id)
        return GroupMessage.objects.create(sender=sender, group=group, content=content)

    @database_sync_to_async
    def mark_as_read(self, message_id):
        """标记消息为已读"""
        try:
            message = Message.objects.get(id=message_id)
            if not message.is_read:
                message.is_read = True
                message.save()
            return message
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_group_chats(self, user_id):
        """获取用户所属的所有群聊ID"""
        return list(
            GroupChat.objects.filter(members=user_id).values_list("id", flat=True)
        )

    @database_sync_to_async
    def check_group_membership(self, user_id, group_id):
        """检查用户是否是群成员"""
        try:
            group = GroupChat.objects.get(id=group_id)
            return group.members.filter(id=user_id).exists()
        except GroupChat.DoesNotExist:
            return False
