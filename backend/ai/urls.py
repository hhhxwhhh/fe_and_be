from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.DeepSeekChatView.as_view(), name="deepseek-chat"),
    path(
        "generate/", views.DeepSeekGenerateTextView.as_view(), name="deepseek-generate"
    ),
]
