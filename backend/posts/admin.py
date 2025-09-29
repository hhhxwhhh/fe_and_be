from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "statistics/",
                self.admin_site.admin_view(self.statistics_view),
                name="posts_statistics",
            ),
        ]
        return custom_urls + urls

    def statistics_view(self, request):
        # 获取帖子相关的统计数据
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        # 总帖数
        total_posts = Post.objects.count()

        # 热门帖子排行
        popular_posts = Post.objects.annotate(comment_count=Count("comments")).order_by(
            "-comment_count"
        )[:5]

        # 发帖趋势（最近7天）
        week_ago = timezone.now() - timedelta(days=7)
        post_trend_data = []
        for i in range(7):
            day = week_ago + timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = Post.objects.filter(
                created_at__gte=day, created_at__lt=next_day
            ).count()
            post_trend_data.append({"date": day.strftime("%Y-%m-%d"), "count": count})

        context = dict(
            self.admin_site.each_context(request),
            total_posts=total_posts,
            popular_posts=popular_posts,
            post_trend_data=post_trend_data,
        )
        return render(request, "admin/posts_statistics.html", context)

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
