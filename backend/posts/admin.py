from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "content_preview", "created_at", "has_image")
    list_filter = ("created_at", "updated_at")
    search_fields = ("author__username", "content")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def has_image(self, obj):
        return obj.image is not None

    has_image.boolean = True
    has_image.short_description = "Has Image"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "content_preview", "created_at", "has_image")
    list_filter = ("created_at",)
    search_fields = ("author__username", "content", "post__content")
    readonly_fields = ("created_at",)

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def has_image(self, obj):
        return obj.image is not None

    has_image.boolean = True
    has_image.short_description = "Has Image"
