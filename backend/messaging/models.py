from django.db import models
from accounts.models import User

# Create your models here.


class Message(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    image = models.ImageField(upload_to="messages/images/", blank=True, null=True)
    file = models.FileField(upload_to="messages/file/", blank=True, null=True)

    is_revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.content[:20]}..."


class GroupChat(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name="group_chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to="group_avatars/", blank=True, null=True)
    created_by = models.ForeignKey(
        User, related_name="created_groups", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(
        GroupChat, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name="group_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="group_messages/images/", blank=True, null=True)
    file = models.FileField(upload_to="group_messages/file/", blank=True, null=True)
    is_revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:20]}..."
