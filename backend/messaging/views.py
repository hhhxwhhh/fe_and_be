from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Message
from accounts.models import User
from .serializers import (
    UserSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
)


class IsParticipant(permissions.BasePermission):
    """只有聊天的成员才能访问"""

    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.recipient == request.user


class IsSender(permissions.BasePermission):
    """只有发送者才能编辑或删除消息"""

    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user


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


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查用户是否有权限编辑消息（只有发送者可以）
        if instance.sender != request.user:
            return Response(
                {"detail": "只有消息发送者可以编辑消息"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = MessageUpdateSerializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        if serializer.is_valid():
            updated_instance = serializer.save(is_edited=True)
            response_serializer = self.get_serializer(updated_instance)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查用户是否有权限删除消息（只有发送者可以）
        if instance.sender != request.user:
            return Response(
                {"detail": "只有消息发送者可以删除消息"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 检查是否尝试给自己发消息
            recipient_id = request.data.get("recipient")
            if str(request.user.id) == str(recipient_id):
                return Response(
                    {"detail": "不能给自己发送消息"}, status=status.HTTP_400_BAD_REQUEST
                )

            # 检查接收者是否存在
            try:
                recipient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                return Response(
                    {"recipient": "接收者不存在"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(sender=request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        # 获取用户头像的完整URL
        avatar_url = None
        if conv["user"].avatar:
            # 使用 request.build_absolute_uri 生成完整URL
            avatar_url = request.build_absolute_uri(conv["user"].avatar.url)

        result.append(
            {
                "user": {
                    "id": conv["user"].id,
                    "username": conv["user"].username,
                    "avatar": avatar_url,
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
    try:
        message = get_object_or_404(Message, id=message_id, recipient=request.user)
        message.is_read = True
        message.save()
        return Response({"status": "message marked as read"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
