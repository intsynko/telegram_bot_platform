from django.contrib import admin
from .models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['telegram_username', 'telegram_user_id', 'bot', 'created_at']
    list_filter = ['bot', 'created_at']
    search_fields = ['telegram_username', 'telegram_user_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['bot']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'text_preview', 'is_user_message', 'created_at']
    list_filter = ['is_user_message', 'created_at', 'chat__bot']
    search_fields = ['text', 'chat__telegram_username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['chat']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'
