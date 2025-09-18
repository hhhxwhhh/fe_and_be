from django.urls import path
from . import views

urlpatterns = [
    path("conversations/", views.conversation_list, name="conversation-list"),
    path(
        "messages/<int:user_id>/", views.MessageListView.as_view(), name="message-list"
    ),
    path("messages/", views.MessageCreateView.as_view(), name="message-create"),
    path(
        "messages/<int:message_id>/read/",
        views.mark_as_read,
        name="message-mark-as-read",
    ),
]
