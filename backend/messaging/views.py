from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Message
from accounts.models import User
from .serializers import UserSerializer, MessageSerializer, MessageCreateSerializer


class IsParticipant(permissions.BasePermission):
    """只有聊天的成员才能访问"""

    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.recipient == request.user


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        user = self.request.user
        user_id = self.kwargs.get("user_id")
        return Message.objects.filter(
            (Q(sender=user) & Q(recipient_id=user_id))
            | (Q(sender_id=user_id) & Q(recipient=user))
        ).select_related("sender", "recipient")


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def conversation_list(request):
    """获取当前用户的所有对话"""
    user = request.user
    sent_messages = Message.objects.filter(sender=user)
    received_messages = Message.objects.filter(recipient=user)

    # 构建对话的列表
    conversations = {}

    for msg in sent_messages:
        recipient_id = msg.recipient.id
        if (
            recipient_id not in conversations
            or msg.timestamp > conversations[recipient_id]["timestamp"]
        ):
            conversations[recipient_id] = {
                "user": msg.recipient,
                "last_message": msg,
                "timestamp": msg.timestamp,
                "unread_count": 0,
            }
    # 处理接受到的信息
    for msg in received_messages:
        sender_id = msg.sender.id
        if (
            sender_id not in conversations
            or msg.timestamp > conversations[sender_id]["timestamp"]
        ):
            unread_count = Message.objects.filter(
                sender_id=sender_id, recipient=user, is_read=False
            ).count()
            conversations[sender_id] = {
                "user": msg.sender,
                "last_message": msg,
                "timestamp": msg.timestamp,
                "unread_count": unread_count,
            }

    conversations_list = list(conversations.values())
    conversations_list.sort(key=lambda x: x["timestamp"], reverse=True)

    # 序列化数据
    result = []
    for conv in conversations_list:
        result.append(
            {
                "user": {
                    "id": conv["user"].id,
                    "username": conv["user"].username,
                    "avatar": conv["user"].avatar.url if conv["user"].avatar else None,
                },
                "last_message": {
                    "content": conv["last_message"].content,
                    "timestamp": conv["last_message"].timestamp,
                    "is_read": conv["last_message"].is_read,
                },
                "unread_count": conv["unread_count"],
            }
        )

    # 添加调试信息
    print(f"User: {user.username}")
    print(f"Conversations result: {result}")

    return Response(result)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, message_id):
    """处理消息，转换为已读"""
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return Response({"status": "message marked as read"})
