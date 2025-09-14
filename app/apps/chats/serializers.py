from rest_framework import serializers
from .models import Chat, Message, FormField


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at', 'is_user_message']


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'name', 'value', 'created_at', 'updated_at']


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    form_fields = FormFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = ['id', 'telegram_user_id', 'telegram_username', 'telegram_chat_id', 'bot', 'context', 'created_at', 'updated_at', 'messages', 'form_fields']
