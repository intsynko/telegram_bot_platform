"""
Фасады для бизнес-логики приложения scenarios
Содержат функции для управления сценариями
"""
from typing import Optional
from django.contrib.auth import get_user_model
from apps.scenarios.models import Scenario

User = get_user_model()


def create_scenario(name: str, owner: User, graph: dict = None) -> Scenario:
    """Создание нового сценария"""
    # TODO: Реализовать в следующем этапе
    pass


def copy_template_scenario(template_id: int, user: User) -> Scenario:
    """Копирование шаблонного сценария"""
    # TODO: Реализовать в следующем этапе
    pass


def update_scenario_graph(scenario: Scenario, graph: dict) -> Scenario:
    """Обновление графа сценария с валидацией"""
    # TODO: Реализовать в следующем этапе
    pass


def delete_user_scenario(scenario_id: int, user: User) -> bool:
    """Удаление сценария с проверкой владельца"""
    # TODO: Реализовать в следующем этапе
    pass