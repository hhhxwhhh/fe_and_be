from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.models import User as DjangoUser
from .models import User
from posts.models import Post
from interactions.models import Like, Notification
from messaging.models import Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_followers_count",
        "get_following_count",
        "avatar_preview",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("date_joined", "last_login", "avatar_preview")
    date_hierarchy = "date_joined"

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "bio",
                    "birth_date",
                    "avatar",
                    "avatar_preview",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Follows", {"fields": ("following",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        from accounts.admin_views import statistics_view
        custom_urls = [
            path('statistics/', statistics_view, name='accounts_statistics'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # 添加统计信息到用户管理页面
        extra_context['statistics'] = {
            'total_users': User.objects.count(),
            'total_posts': Post.objects.count(),
            'total_likes': Like.objects.count(),
            'total_messages': Message.objects.count(),
        }
        
        return super().changelist_view(request, extra_context)

    def get_followers_count(self, obj):
        return obj.followers.count()

    get_followers_count.short_description = "Followers"

    def get_following_count(self, obj):
        return obj.following.count()

    get_following_count.short_description = "Following"

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height:50px; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "No Avatar"

    avatar_preview.short_description = "Avatar Preview"