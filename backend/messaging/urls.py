from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import consumers

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r"group-chats", views.GroupChatViewSet, basename="group-chat")
router.register(r"group-messages", views.GroupMessageViewSet, basename="group-message")

urlpatterns = [
    path("conversations/", views.conversation_list, name="conversation-list"),
    path(
        "conversations/<int:user_id>/",
        views.MessageListView.as_view(),
        name="message-list",
    ),
    path("messages/", views.MessageCreateView.as_view(), name="message-create"),
    path(
        "messages/<int:message_id>/read/",
        views.mark_as_read,
        name="message-mark-as-read",
    ),
    path("messages/<int:pk>/revoke/", views.revoke_message, name="message-revoke"),
    path(
        "messages/<int:pk>/", views.MessageDetailView.as_view(), name="message-detail"
    ),
    path("", include(router.urls)),
]

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
]
