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
    return Scenario.objects.filter(owner=user, is_template=False)


def get_template_scenarios() -> QuerySet[Scenario]:
    """Получить все шаблонные сценарии"""
    return Scenario.objects.filter(is_template=True)


def get_scenario_with_access_check(scenario_id: int, user: User) -> Optional[Scenario]:
    """Получить сценарий с проверкой доступа"""
    try:
        return Scenario.objects.get(id=scenario_id, owner=user, is_template=False)
    except Scenario.DoesNotExist:
        return None


def get_template_scenario(template_id: int) -> Optional[Scenario]:
    """Получить шаблонный сценарий"""
    try:
        return Scenario.objects.get(id=template_id, is_template=True)
    except Scenario.DoesNotExist:
        return None