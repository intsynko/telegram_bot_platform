"""
Селекторы для запросов к БД приложения chats
Содержат функции для получения данных чатов, сообщений и полей форм
"""
from typing import Optional, List
from django.db.models import QuerySet
from apps.chats.models import Chat, Message, FormField


def get_bot_chats_with_pagination(bot_id: int, page: int, page_size: int) -> dict:
    """Получить чаты бота с пагинацией и динамическими полями"""
    # TODO: Реализовать в следующем этапе
    pass


def get_chat_with_relations(chat_id: int) -> Optional[Chat]:
    """Получить чат с сообщениями и полями формы"""
    # TODO: Реализовать в следующем этапе
    pass


def get_chat_messages(chat_id: int) -> QuerySet[Message]:
    """Получить сообщения чата"""
    # TODO: Реализовать в следующем этапе
    pass


def get_chat_form_fields(chat_id: int) -> QuerySet[FormField]:
    """Получить поля формы чата"""
    # TODO: Реализовать в следующем этапе
    pass


def get_unique_form_field_names(bot_id: int) -> List[str]:
    """Получить все уникальные названия полей формы для бота"""
    # TODO: Реализовать в следующем этапе
    pass