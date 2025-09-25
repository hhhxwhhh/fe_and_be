from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Message, GroupMessage, GroupChat
from accounts.models import User
from .serializers import (
    UserSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    GroupChatSerializer,
    GroupMessageCreateSerializer,
    GroupMessageSerializer,
)


class IsParticipant(permissions.BasePermission):
    """只有聊天的成员才能访问"""

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            return obj.recipient == request.user or obj.sender == request.user
        elif isinstance(obj, GroupMessage):
            return obj.group.members.filter(id=request.user.id).exists()
        elif isinstance(obj, GroupChat):
            return obj.members.filter(id=request.user.id).exists()
        return False


class IsSender(permissions.BasePermission):
    """只有发送者才能编辑或删除消息"""

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Message):
            return obj.sender == request.user
        elif isinstance(obj, GroupMessage):
            return obj.sender == request.user
        return False


class GroupChatViewSet(viewsets.ModelViewSet):
    serializer_class = GroupChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return GroupChat.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        group.members.add(self.request.user)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """添加成员到群聊"""
        group = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "需要提供用户ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            group.members.add(user)
            return Response(
                {"detail": "用户已成功添加到群聊"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        """从群聊中移除成员"""
        group = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "需要提供用户ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 不能移除自己，除非是群主
        if int(user_id) == request.user.id and group.created_by != request.user:
            return Response(
                {"detail": "普通成员不能移除自己"}, status=status.HTTP_403_FORBIDDEN
            )

        # 群主可以移除任何人，包括自己
        # 其他成员只能移除自己
        try:
            user = User.objects.get(id=user_id)
            if group.created_by == request.user or int(user_id) == request.user.id:
                group.members.remove(user)
                return Response(
                    {"detail": "用户已成功从群聊中移除"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "您没有权限移除该用户"}, status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            return Response({"detail": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


class GroupMessageViewSet(viewsets.ModelViewSet):
    """群聊消息视图集"""

    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        group_id = self.request.query_params.get("group_id", None)
        if group_id:
            return GroupMessage.objects.filter(group_id=group_id)
        return GroupMessage.objects.filter(group__members=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return GroupMessageCreateSerializer
        return GroupMessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def revoke_message(request, pk):
    try:
        message = Message.objects.get(pk=pk)
    except Message.DoesNotExist:
        return Response(
            {"detail": "消息不存在"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if message.sender != request.user:
        return Response(
            {"detail": "只有消息发送者可以撤回消息"},
            status=status.HTTP_403_FORBIDDEN,
        )
    if message.is_revoked:
        return Response(
            {"detail": "消息已经被撤回"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    time_diff = timezone.now() - message.timestamp
    if time_diff.total_seconds() > 120:  # 2分钟 = 120秒
        return Response(
            {"detail": "消息发送超过2分钟，无法撤回"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 添加检查确保消息不是空的
    if not message.content and not message.image and not message.file:
        return Response(
            {"detail": "无法撤回空消息"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    message.is_revoked = True
    message.save()

    serializer = MessageSerializer(message, context={"request": request})
    return Response(serializer.data)


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        user = self.request.user
        user_id = self.kwargs.get("user_id")

        # 添加分页支持
        queryset = (
            Message.objects.filter(
                (Q(sender=user) & Q(recipient_id=user_id))
                | (Q(sender_id=user_id) & Q(recipient=user))
            )
            .select_related("sender", "recipient")
            .order_by("-timestamp")
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # 获取分页参数
        page = self.request.query_params.get("page", 1)
        page_size = self.request.query_params.get("page_size", 20)

        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page = 1
            page_size = 20

        # 应用分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_queryset = queryset[start:end]

        serializer = self.get_serializer(paginated_queryset, many=True)

        # 返回分页信息
        return Response(
            {
                "results": serializer.data,
                "count": queryset.count(),
                "page": page,
                "page_size": page_size,
                "has_next": end < queryset.count(),
                "has_previous": page > 1,
            }
        )


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
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # 增加部分的调试的日志
        print("Received request data :", request.data)
        print("content type :", request.content_type)
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
            # 打印错误信息以便调试
            print("Message creation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def conversation_list(request):
    """获取当前用户的所有对话，包括私聊和群聊"""
    user = request.user

    # 获取私聊对话
    sent_messages = Message.objects.filter(sender=user)
    received_messages = Message.objects.filter(recipient=user)

    # 构建私聊对话列表
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

    # 处理接收到的信息
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

    # 序列化私聊数据
    private_chats = []
    for conv in conversations_list:
        # 获取用户头像的完整URL
        avatar_url = None
        if conv["user"].avatar:
            # 使用 request.build_absolute_uri 生成完整URL
            avatar_url = request.build_absolute_uri(conv["user"].avatar.url)

        private_chats.append(
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

    # 获取群聊列表
    group_chats = GroupChat.objects.filter(members=user).prefetch_related("members")
    group_chats_data = []
    for group in group_chats:
        # 获取群聊最新的消息
        latest_message = group.messages.order_by("-timestamp").first()

        avatar_url = None
        if group.avatar:
            avatar_url = request.build_absolute_uri(group.avatar.url)

        group_data = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "avatar": avatar_url,
            "member_count": group.members.count(),
            "created_at": group.created_at,
            "last_message": None,
        }

        if latest_message:
            group_data["last_message"] = {
                "content": latest_message.content,
                "timestamp": latest_message.timestamp,
                "sender": {
                    "id": latest_message.sender.id,
                    "username": latest_message.sender.username,
                },
            }

        group_chats_data.append(group_data)

    return Response({"private_chats": private_chats, "group_chats": group_chats_data})


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
