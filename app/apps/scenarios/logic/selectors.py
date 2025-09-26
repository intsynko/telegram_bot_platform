"""
Селекторы для запросов к БД приложения scenarios
Содержат функции для получения данных сценариев
"""
from typing import Optional
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from apps.scenarios.models import Scenario

User = get_user_model()


def get_user_scenarios(user: User) -> QuerySet[Scenario]:
    """Получить сценарии пользователя (не шаблоны)"""
    # TODO: Реализовать в следующем этапе
    pass


def get_template_scenarios() -> QuerySet[Scenario]:
    """Получить все шаблонные сценарии"""
    # TODO: Реализовать в следующем этапе
    pass


def get_scenario_with_access_check(scenario_id: int, user: User) -> Optional[Scenario]:
    """Получить сценарий с проверкой доступа"""
    # TODO: Реализовать в следующем этапе
    pass


def get_template_scenario(template_id: int) -> Optional[Scenario]:
    """Получить шаблонный сценарий"""
    # TODO: Реализовать в следующем этапе
    pass