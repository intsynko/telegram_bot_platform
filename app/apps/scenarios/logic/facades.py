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
    scenario = Scenario.objects.create(
        name=name,
        owner=owner,
        graph=graph or {},
        is_template=False
    )
    return scenario


def copy_template_scenario(template_id: int, user: User) -> Scenario:
    """Копирование шаблонного сценария"""
    try:
        template = Scenario.objects.get(id=template_id, is_template=True)
        new_scenario = Scenario.objects.create(
            graph=template.graph,
            name=f"{template.name} - Копия",
            owner=user,
            is_template=False
        )
        return new_scenario
    except Scenario.DoesNotExist:
        raise ValueError(f"Template scenario with id {template_id} not found")


def update_scenario_graph(scenario: Scenario, graph: dict) -> Scenario:
    """Обновление графа сценария с валидацией"""
    scenario.graph = graph
    scenario.save()
    return scenario


def delete_user_scenario(scenario_id: int, user: User) -> bool:
    """Удаление сценария с проверкой владельца"""
    try:
        scenario = Scenario.objects.get(id=scenario_id, owner=user, is_template=False)
        scenario.delete()
        return True
    except Scenario.DoesNotExist:
        return False