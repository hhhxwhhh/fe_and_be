from django.contrib import admin
from .models import Like, Notification


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "post__content")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("user", "post")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "actor",
        "notification_type",
        "is_read",
        "created_at",
        "content_preview",
    )
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__username", "actor__username", "comment")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    list_editable = ("is_read",)
    raw_id_fields = ("recipient", "actor", "post")

    def content_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
        return "No content"

    content_preview.short_description = "Comment Preview"
