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


class ChatWithDynamicFieldsSerializer(serializers.ModelSerializer):
    """Сериализатор чата с динамическими полями форм"""
    
    def to_representation(self, instance):
        """Добавляем динамические поля форм в ответ"""
        data = {
            'id': instance.id,
            'telegram_user_id': instance.telegram_user_id,
            'telegram_username': instance.telegram_username,
            'telegram_chat_id': instance.telegram_chat_id,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'context': instance.context
        }
        
        # Получаем все поля формы для этого чата
        form_fields_dict = {field.name: field.value for field in instance.form_fields.all()}
        
        # Получаем все уникальные поля форм для бота из контекста
        form_field_names = self.context.get('form_field_names', [])
        
        # Добавляем динамические поля
        for field_name in form_field_names:
            data[f'field_{field_name}'] = form_fields_dict.get(field_name, '')
        
        return data
    
    class Meta:
        model = Chat
        fields = ['id', 'telegram_user_id', 'telegram_username', 'telegram_chat_id', 'context', 'created_at', 'updated_at']
