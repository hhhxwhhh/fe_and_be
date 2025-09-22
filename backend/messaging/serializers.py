from rest_framework import serializers
from .models import Message
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "recipient",
            "content",
            "timestamp",
            "is_read",
            "updated_at",
            "is_edited",
            "file",
            "image",
            "is_revoked",
        ]
        read_only_fields = ["sender", "timestamp", "updated_at", "is_edited"]


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["recipient", "content", "file", "image"]
        extra_kwargs = {"content": {"required": False}}

    def validate(self, data):
        if not (data.get("content") or data.get("file") or data.get("image")):
            raise serializers.ValidationError("发送的内容不能为空")
        return data

    def validate_file(self, value):
        if value:
            # 检查文件大小 (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("文件大小不能超过10MB")

            # 检查文件类型 - 添加PDF和其他常用文档类型
            allowed_types = [
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"不支持的文件类型: {value.content_type}. 支持的类型: PDF, Word, Excel, 文本文件"
                )

        return value

    def validate_image(self, value):
        if value:
            # 检查文件大小 (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("图片大小不能超过10MB")

            # 检查图片类型
            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/bmp",
                "image/webp",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"不支持的图片类型: {value.content_type}. 支持的类型: JPG, PNG, GIF, BMP, WebP"
                )

        return value


class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content", "image", "file"]
