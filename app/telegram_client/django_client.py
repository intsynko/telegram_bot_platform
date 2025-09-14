import os
import sys
import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.scenarios.models import Scenario
from apps.bots.models import Bot
from apps.chats.models import Chat, Message, FormField


@sync_to_async
def get_scenario_by_bot(bot_id):
    return Scenario.objects.get(bots__id=bot_id)

def get_bot_by_id(bot_id):
    return Bot.objects.get(id=bot_id)

@sync_to_async
def get_scenario_by_id(scenario_id):
    return Scenario.objects.get(id=scenario_id)


@sync_to_async
def get_or_create_chat(telegram_user_id, telegram_username, telegram_chat_id, bot_id, context=None):
    """Получить или создать чат для пользователя"""
    chat, created = Chat.objects.get_or_create(
        telegram_chat_id=telegram_chat_id,
        bot_id=bot_id,
        defaults={
            'telegram_user_id': telegram_user_id,
            'telegram_username': telegram_username,
            'context': context or {}
        }
    )
    return chat, created


@sync_to_async
def create_message(chat_id, text, is_user_message=True):
    """Создать сообщение в чате"""
    message = Message.objects.create(
        chat_id=chat_id,
        text=text,
        is_user_message=is_user_message
    )
    return message


@sync_to_async
def update_chat_context(chat_id, context):
    """Обновить контекст чата"""
    chat = Chat.objects.get(id=chat_id)
    chat.context = context
    chat.save()
    return chat


@sync_to_async
def get_chat_by_telegram_data(telegram_chat_id, bot_id):
    """Получить чат по telegram_chat_id и bot_id"""
    try:
        return Chat.objects.get(telegram_chat_id=telegram_chat_id, bot_id=bot_id)
    except Chat.DoesNotExist:
        return None


@sync_to_async
def save_or_update_form_field(chat_id, field_name, field_value):
    """Сохранить или обновить значение поля формы"""
    form_field, created = FormField.objects.get_or_create(
        chat_id=chat_id,
        name=field_name,
        defaults={'value': field_value}
    )
    if not created:
        form_field.value = field_value
        form_field.save()
    return form_field


@sync_to_async
def get_form_fields_by_chat(chat_id):
    """Получить все поля формы для чата"""
    return list(FormField.objects.filter(chat_id=chat_id).order_by('created_at'))


@sync_to_async
def get_form_field_value(chat_id, field_name):
    """Получить значение конкретного поля формы"""
    try:
        form_field = FormField.objects.get(chat_id=chat_id, name=field_name)
        return form_field.value
    except FormField.DoesNotExist:
        return None
