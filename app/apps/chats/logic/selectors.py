"""
Селекторы для запросов к БД приложения chats
Содержат функции для получения данных чатов, сообщений и полей форм
"""
from typing import Optional, List
from django.db.models import QuerySet
from django.core.paginator import Paginator
from apps.chats.models import Chat, Message, FormField
from apps.bots.models import Bot


def get_bot_chats_with_pagination(bot_id: int, page: int, page_size: int) -> dict:
    """Получить чаты бота с пагинацией и динамическими полями"""
    # Проверяем, что бот существует
    try:
        bot = Bot.objects.get(id=bot_id)
    except Bot.DoesNotExist:
        raise ValueError(f"Bot with id {bot_id} not found")
    
    # Получаем чаты с связанными данными
    chats = Chat.objects.filter(
        bot_id=bot_id
    ).prefetch_related('form_fields', 'messages').order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(chats, page_size)
    page_obj = paginator.get_page(page)
    
    # Получаем все уникальные поля формы для этого бота
    form_field_names = get_unique_form_field_names(bot_id)
    
    # Подготавливаем данные для каждого чата
    results = []
    for chat in page_obj.object_list:
        # Базовые данные чата
        chat_data = {
            'id': chat.id,
            'telegram_user_id': chat.telegram_user_id,
            'telegram_username': chat.telegram_username,
            'telegram_chat_id': chat.telegram_chat_id,
            'created_at': chat.created_at,
            'updated_at': chat.updated_at,
            'context': chat.context
        }
        
        # Добавляем данные полей формы
        form_fields_dict = {field.name: field.value for field in chat.form_fields.all()}
        for field_name in form_field_names:
            chat_data[f'field_{field_name}'] = form_fields_dict.get(field_name, '')
        
        results.append(chat_data)
    
    return {
        'results': results,
        'form_fields': form_field_names,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    }


def get_chat_with_relations(chat_id: int) -> Optional[Chat]:
    """Получить чат с сообщениями и полями формы"""
    try:
        return Chat.objects.prefetch_related(
            'form_fields', 'messages'
        ).get(id=chat_id)
    except Chat.DoesNotExist:
        return None


def get_chat_messages(chat_id: int) -> QuerySet[Message]:
    """Получить сообщения чата"""
    return Message.objects.filter(chat_id=chat_id).order_by('created_at')


def get_chat_form_fields(chat_id: int) -> QuerySet[FormField]:
    """Получить поля формы чата"""
    return FormField.objects.filter(chat_id=chat_id).order_by('created_at')


def get_unique_form_field_names(bot_id: int) -> List[str]:
    """Получить все уникальные названия полей формы для бота"""
    form_field_names = FormField.objects.filter(
        chat__bot_id=bot_id
    ).values_list('name', flat=True).distinct().order_by('name')
    return list(form_field_names)


def get_bot_chats_queryset(bot_id: int) -> QuerySet[Chat]:
    """Получить базовый queryset чатов бота для стандартной DRF пагинации"""
    from rest_framework.exceptions import NotFound
    
    try:
        # Проверяем, что бот существует
        Bot.objects.get(id=bot_id)
    except Bot.DoesNotExist:
        raise NotFound(f"Bot with id {bot_id} not found")
    
    return Chat.objects.filter(
        bot_id=bot_id
    ).prefetch_related('form_fields', 'messages').order_by('-created_at')


def get_chat_by_telegram_data(telegram_chat_id: int, bot_id: int) -> Optional[Chat]:
    """Получить чат по telegram_chat_id и bot_id"""
    try:
        return Chat.objects.get(telegram_chat_id=telegram_chat_id, bot_id=bot_id)
    except Chat.DoesNotExist:
        return None


def get_form_field_value(chat_id: int, field_name: str) -> Optional[str]:
    """Получить значение конкретного поля формы"""
    try:
        form_field = FormField.objects.get(chat_id=chat_id, name=field_name)
        return form_field.value
    except FormField.DoesNotExist:
        return None


def get_chat_context_data(telegram_chat_id: int, bot_id: int) -> Optional[dict]:
    """Получить контекст чата для восстановления состояния бота"""
    try:
        chat = Chat.objects.get(telegram_chat_id=telegram_chat_id, bot_id=bot_id)
        return {
            'chat_id': chat.id,
            'context': chat.context,
            'telegram_user_id': chat.telegram_user_id,
            'telegram_username': chat.telegram_username
        }
    except Chat.DoesNotExist:
        return None


def get_chat_form_fields_dict(chat_id: int) -> dict:
    """Получить все поля формы для чата в виде словаря"""
    try:
        form_fields = FormField.objects.filter(chat_id=chat_id)
        return {field.name: field.value for field in form_fields}
    except Exception:
        return {}