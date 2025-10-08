from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer 

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 
    
    # 1. 直接递归引用自身来处理 replies
    #    read_only=True 意味着它只在输出时生效
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "post", "author", "content", "image", "created_at", "parent", "replies")
        # 'parent' 字段现在由 DRF 自动处理，我们不需要在 read_only_fields 里特别声明
        read_only_fields = ("id", "author", "created_at", "post") 
        extra_kwargs = {
            "content": {"required": False, "allow_blank": True},
            # 让 parent 字段在 API 文档中可见，并且是可选的
            "parent": {"write_only": True, "required": False, "allow_null": True},
        }

    def get_replies(self, obj):
        # 使用 self.__class__ (也就是 CommentSerializer 自己) 来序列化子评论
        queryset = obj.replies.all().order_by('created_at')
        serializer = self.__class__(queryset, many=True, context=self.context)
        return serializer.data

    def validate(self, data):
        if not (data.get("content", "").strip() or data.get("image")):
            raise serializers.ValidationError("评论不能完全为空")
        return data

    # 2. 添加 create 方法，自动设置 author
    def create(self, validated_data):
        # 从 context 中获取 request 对象
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # 自动将当前登录用户设置为作者
            validated_data['author'] = request.user
        
        # 调用父类的 create 方法来创建对象
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if instance.image and request:
            representation["image"] = request.build_absolute_uri(instance.image.url)
        return representation


class PostSerializer(serializers.ModelSerializer): 
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id", "author", "author_id", "is_following", "content", "image",
            "created_at", "updated_at", "comments", "likes_count", "is_liked",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at", "author_id")

    def get_comments(self, obj):
        # 逻辑保持不变，只获取顶层评论
        top_level_comments = obj.comments.filter(parent__isnull=True).order_by('created_at')
        request = self.context.get("request")
        return CommentSerializer(top_level_comments, many=True, context={'request': request}).data

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
            # 假设你的 User 模型有 'following' 这个多对多字段
            return request.user.following.filter(id=obj.author.id).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if instance.image and request:
            representation["image"] = request.build_absolute_uri(instance.image.url)
        return representation