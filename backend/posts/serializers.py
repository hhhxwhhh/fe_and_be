from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSeralizers(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "image", "created_at")
        read_only_fields = ("id", "author", "created_at")

        extra_kwargs = {"content": {"required": False, "allow_blank": True}}

    def validate(self, data):
        if not (data.get("content", "").strip() or data.get("image")):
            raise serializers.ValidationError("评论不能完全为空")
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if instance.image and request:
            representation["image"] = request.build_absolute_uri(instance.image.url)
        return representation


class PostSeralizers(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    comments = CommentSeralizers(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_id",
            "is_following",
            "content",
            "image",
            "created_at",
            "updated_at",
            "comments",
            "likes_count",
            "is_liked",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at", "author_id")

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return request.user.following.filter(id=obj.author.id).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if instance.image and request:
            representation["image"] = request.build_absolute_uri(instance.image.url)
        return representation
