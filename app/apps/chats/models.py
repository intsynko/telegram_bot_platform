from django.db import models
from apps.bots.models import Bot


class Chat(models.Model):
    telegram_user_id = models.BigIntegerField(verbose_name="Telegram User ID")
    telegram_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telegram Username")
    telegram_chat_id = models.BigIntegerField(verbose_name="Telegram Chat ID")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='chats', verbose_name="Bot")
    context = models.JSONField(default=dict, blank=True, verbose_name="Context")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        unique_together = ['telegram_chat_id', 'bot']

    def __str__(self):
        username = f"@{self.telegram_username}" if self.telegram_username else f"User {self.telegram_user_id}"
        return f"{username} - {self.bot.name}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name="Chat")
    text = models.TextField(verbose_name="Message Text")
    is_user_message = models.BooleanField(default=True, verbose_name="Is User Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def __str__(self):
        message_type = "User" if self.is_user_message else "Bot"
        return f"{message_type}: {self.text[:50]}{'...' if len(self.text) > 50 else ''}"
