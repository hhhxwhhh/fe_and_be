from django.contrib import admin
from .models import Message, GroupChat, GroupMessage


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "sender",
        "recipient",
        "timestamp",
        "is_read",
        "is_edited",
        "has_attachment",
    ]
    list_filter = ["timestamp", "is_read", "is_edited", "is_revoked"]
    search_fields = ["sender__username", "recipient__username", "content"]
    readonly_fields = ["timestamp", "updated_at"]

    def has_attachment(self, obj):
        return obj.image is not None or obj.file is not None

    has_attachment.boolean = True
    has_attachment.short_description = "Has Attachment"


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "member_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "created_by__username", "members__username"]
    filter_horizontal = ["members"]
    readonly_fields = ["created_at", "updated_at"]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Members"


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "group", "content_preview", "timestamp", "is_edited"]
    list_filter = ["timestamp", "is_edited", "is_revoked"]
    search_fields = ["sender__username", "group__name", "content"]
    readonly_fields = ["timestamp", "updated_at"]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"
