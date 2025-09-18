from django.contrib import admin
from .models import Message

# Register your models here.


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "recipient", "timestamp", "is_read"]
    list_filter = ["timestamp", "is_read"]
    search_fields = ["sender__username", "recipient__username", "content"]
