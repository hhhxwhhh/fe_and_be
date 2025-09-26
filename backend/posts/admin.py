from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "content_preview",
        "created_at",
        "has_image",
        "comment_count",
        "like_count",
    )
    list_filter = ("created_at", "updated_at", "author")
    search_fields = ("author__username", "content")
    readonly_fields = ("created_at", "updated_at", "image_preview")
    date_hierarchy = "created_at"
    raw_id_fields = ("author",)

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def has_image(self, obj):
        return obj.image is not None

    has_image.boolean = True
    has_image.short_description = "Has Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height:200px;" />',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Image Preview"

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Comments"

    def like_count(self, obj):
        return obj.likes.count()

    like_count.short_description = "Likes"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "post",
        "content_preview",
        "created_at",
        "has_image",
    )
    list_filter = ("created_at", "author")
    search_fields = ("author__username", "content", "post__content")
    readonly_fields = ("created_at", "image_preview")
    raw_id_fields = ("author", "post")

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def has_image(self, obj):
        return obj.image is not None

    has_image.boolean = True
    has_image.short_description = "Has Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height:200px;" />',
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Image Preview"
