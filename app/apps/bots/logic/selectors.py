"""
Селекторы для запросов к БД приложения bots
Содержат функции для получения данных ботов
"""
from typing import Optional
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from apps.bots.models import Bot
from apps.bots.bot_manager import is_bot_running

User = get_user_model()


def get_user_bots(user: User) -> QuerySet[Bot]:
    """Получить всех ботов пользователя"""
    return Bot.objects.filter(owner=user)


def get_bot_with_scenario(bot_id: int, user: User) -> Optional[Bot]:
    """Получить бота со сценарием с проверкой владельца"""
    try:
        return Bot.objects.select_related('scenario').get(id=bot_id, owner=user)
    except Bot.DoesNotExist:
        return None


def get_bot_status(bot_id: int) -> dict:
    """Получить статус бота (запущен/остановлен)"""
    return {
        'is_running': is_bot_running(bot_id),
        'bot_id': bot_id
    }