"""
Фасады для бизнес-логики приложения bots
Содержат функции для управления ботами
"""
from typing import Optional
from django.contrib.auth import get_user_model
from apps.bots.models import Bot
from apps.scenarios.models import Scenario
from apps.bots.bot_manager import start_bot, stop_bot

User = get_user_model()


def create_bot(name: str, token: str, owner: User, description: str = "") -> Bot:
    """Создание нового бота с валидацией токена"""
    bot = Bot.objects.create(
        name=name,
        token=token,
        owner=owner,
        description=description
    )
    return bot


def start_bot_instance(bot_id: int) -> bool:
    """Запуск бота с проверкой наличия сценария"""
    try:
        bot = Bot.objects.get(id=bot_id)
        if not bot.scenario:
            return False
        return start_bot(bot_id)
    except Bot.DoesNotExist:
        return False


def stop_bot_instance(bot_id: int) -> bool:
    """Остановка бота"""
    return stop_bot(bot_id)


def assign_scenario_to_bot(bot: Bot, scenario: Scenario) -> Bot:
    """Привязка сценария к боту с валидацией"""
    bot.scenario = scenario
    bot.save()
    return bot


def validate_bot_scenario(bot: Bot) -> bool:
    """Проверка готовности бота к запуску"""
    return bot.scenario is not None