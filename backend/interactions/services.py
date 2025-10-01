from .models import Notification
from posts.models import Post
from accounts.models import User

class NotificationService:
    @staticmethod
    def create_like_notification(like_instance):
        """完成点赞通知的创建"""
        if like_instance.user!=like_instance.post.author:
            Notification.objects.create(
                recipient=like_instance.post.author,
                actor=like_instance.user,
                notification_type='like',
                post=like_instance.post,
            )

    @staticmethod
    def create_comment_notification(comment_instance):
        """完成评论通知的创建"""
        if comment_instance.author!=comment_instance.post.author:
            Notification.objects.create(
                recipient=comment_instance.post.author,
                actor=comment_instance.author,
                notification_type='comment',
                post=comment_instance.post,
                comment=comment_instance.content,
            )

    @staticmethod
    def create_follow_notification(follower,followed):
        """完成关注通知的创建"""
        if followed!=follower:
            Notification.objects.create(
                recipient=followed,
                actor=follower,
                notification_type='follow',
            )
        