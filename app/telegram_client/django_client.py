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
from apps.chats.logic import facades, selectors


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
    bot = Bot.objects.get(id=bot_id)
    return facades.get_or_create_chat(
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
        bot=bot,
        username=telegram_username,
        context=context
    )


@sync_to_async
def create_message(chat_id, text, is_user_message=True):
    """Создать сообщение в чате"""
    return facades.add_message_to_chat(
        chat_id=chat_id,
        text=text,
        is_user=is_user_message
    )


@sync_to_async
def update_chat_context(chat_id, context):
    """Обновить контекст чата"""
    chat = Chat.objects.get(id=chat_id)
    return facades.update_chat_context(chat, context)


@sync_to_async
def get_chat_by_telegram_data(telegram_chat_id, bot_id):
    """Получить чат по telegram_chat_id и bot_id"""
    return selectors.get_chat_by_telegram_data(telegram_chat_id, bot_id)


@sync_to_async
def save_or_update_form_field(chat_id, field_name, field_value):
    """Сохранить или обновить значение поля формы"""
    return facades.add_form_field(chat_id, field_name, field_value)


@sync_to_async
def get_form_fields_by_chat(chat_id):
    """Получить все поля формы для чата"""
    return list(selectors.get_chat_form_fields(chat_id))


@sync_to_async
def get_form_field_value(chat_id, field_name):
    """Получить значение конкретного поля формы"""
    return selectors.get_form_field_value(chat_id, field_name)


@sync_to_async
def get_chat_context(telegram_chat_id, bot_id):
    """Получить контекст чата для восстановления состояния бота"""
    return selectors.get_chat_context_data(telegram_chat_id, bot_id)


@sync_to_async
def get_chat_form_fields(chat_id):
    """Получить все поля формы для чата"""
    return selectors.get_chat_form_fields_dict(chat_id)
