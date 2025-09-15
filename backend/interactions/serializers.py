from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True)
    post_cotent = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "actor",
            "notification_type",
            "post",
            "post_content",
            "comment",
            "is_read",
            "created_at",
        )
        read_only_fields = ("id", "actor", "created_at")

    def get_post_content(self, obj):
        if obj.post:
            return (
                obj.post.content[:50] + "..."
                if len(obj.post.content) > 50
                else obj.post.content
            )
        return None
