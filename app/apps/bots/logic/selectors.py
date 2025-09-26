"""
Селекторы для запросов к БД приложения bots
Содержат функции для получения данных ботов
"""
from typing import Optional
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from apps.bots.models import Bot

User = get_user_model()


def get_user_bots(user: User) -> QuerySet[Bot]:
    """Получить всех ботов пользователя"""
    # TODO: Реализовать в следующем этапе
    pass


def get_bot_with_scenario(bot_id: int, user: User) -> Optional[Bot]:
    """Получить бота со сценарием с проверкой владельца"""
    # TODO: Реализовать в следующем этапе
    pass


def get_bot_status(bot_id: int) -> dict:
    """Получить статус бота (запущен/остановлен)"""
    # TODO: Реализовать в следующем этапе
    pass