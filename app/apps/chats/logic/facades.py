"""
Фасады для бизнес-логики приложения chats
Содержат функции для управления чатами, сообщениями и полями форм
"""
from typing import Optional
from apps.bots.models import Bot
from apps.chats.models import Chat, Message, FormField


def create_chat(
    telegram_user_id: int, 
    telegram_chat_id: int, 
    bot: Bot, 
    username: str = None
) -> Chat:
    """Создание нового чата"""
    chat = Chat.objects.create(
        telegram_user_id=telegram_user_id,
        telegram_chat_id=telegram_chat_id,
        telegram_username=username,
        bot=bot,
        context={}
    )
    return chat


def update_chat_context(chat: Chat, context: dict) -> Chat:
    """Обновление контекста чата"""
    chat.context = context
    chat.save()
    return chat


def add_message_to_chat(chat_id: int, text: str, is_user: bool) -> Message:
    """Добавление сообщения в чат"""
    try:
        chat = Chat.objects.get(id=chat_id)
        message = Message.objects.create(
            chat=chat,
            text=text,
            is_user_message=is_user
        )
        return message
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")


def add_form_field(chat_id: int, name: str, value: str) -> FormField:
    """Добавление/обновление поля формы"""
    try:
        chat = Chat.objects.get(id=chat_id)
        form_field, created = FormField.objects.update_or_create(
            chat=chat,
            name=name,
            defaults={'value': value}
        )
        return form_field
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")


def get_or_create_chat(
    telegram_user_id: int,
    telegram_chat_id: int,
    bot: Bot,
    username: str = None,
    context: dict = None
) -> tuple[Chat, bool]:
    """Получить или создать чат для пользователя"""
    chat, created = Chat.objects.get_or_create(
        telegram_chat_id=telegram_chat_id,
        bot=bot,
        defaults={
            'telegram_user_id': telegram_user_id,
            'telegram_username': username,
            'context': context or {}
        }
    )
    return chat, created