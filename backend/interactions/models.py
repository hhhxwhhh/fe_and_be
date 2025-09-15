from django.db import models
from django.conf import settings
from posts.models import Post


# Create your models here.
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("like", "like"),
        ("comment", "comment"),
        ("follow", "follow"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="actions", on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(
        Post,
        related_name="notification",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    comment = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor.username} {self.notification_type} on{self.post}"
