from rest_framework import serializers
from .models import Post,Comment
from django.contrib.auth import get_user_model

User=get_user_model()
class CommentSeralizers(serializers.ModelSerializer):
    author=serializers.StringRelatedField(read_only=True)
    class Meta:
        model=Comment
        fields=('id','author','content','created_at')
        read_only_fields=('id','author','created_at')

class PostSeralizers(serializers.ModelSerializer):
    author=serializers.StringRelatedField(read_only=True)
    comments=CommentSeralizers(many=True,read_only=True)
    likes_count=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()

    class Meta:
        model=Post
        fields=('id','author','content','image','created_at','updated_at','comments','likes_count','is_liked')
        read_only_fields=('id','author','created_at','updated_at')

    def get_likes_count(self,obj):
        return obj.likes.count()
    def get_is_liked(self,obj):
        request=self.context.get('request')
        if request and hasattr(request,'user') and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False