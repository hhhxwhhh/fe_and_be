# backend/accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# 1. 这是一个基础的、不依赖任何其他应用的 UserSerializer
#    它可以被其他任何应用（比如 posts）安全地导入
class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        # 只包含最基础、最通用的字段
        fields = ['id', 'username', 'bio', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


# 2. 这是你原来的 UserSeralizer，我们重命名为 UserDetailSerializer
#    因为它包含了更详细的信息，并且依赖 PostSerializer
class UserDetailSerializer(serializers.ModelSerializer):
    # 3. 把导入语句移动到类的内部，实现“延迟导入”，打破循环！
    from posts.serializers import PostSerializer

    password = serializers.CharField(write_only=True, required=False)
    posts = PostSerializer(many=True, read_only=True) # 注意修正拼写
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "bio", "birth_date", "avatar",
            "followers_count", "following_count", "is_following", "posts", "password",
        )
        read_only_fields = ("id",)

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False

    def create(self, validated_data):
        # 这个 create 方法可能不再需要，因为注册有专门的 Serializer
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# --- 你其他的 Serializer 保持不变 ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被使用")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "bio", "birth_date", "avatar")