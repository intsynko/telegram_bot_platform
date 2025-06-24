import os
import sys
import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.scenarios.models import Scenario
from apps.forms.models import FormField, Form
from apps.menu.models import MenuField, Menu



@sync_to_async
def get_first_scenario():
    return Scenario.objects.first()

@sync_to_async
def get_scenario_by_id(scenario_id):
    return Scenario.objects.get(id=scenario_id)

@sync_to_async
def get_elements_for_scenario(scenario):
    return list(scenario.elements.order_by('order'))

@sync_to_async
def get_form(form_id):
    return Form.objects.get(id=form_id)

@sync_to_async
def get_fields_for_form(form_id):
    return list(FormField.objects.filter(form_id=form_id, hidden=False))


@sync_to_async
def get_fields_for_menu(menu_id):
    return list(MenuField.objects.filter(menu_id=menu_id))

@sync_to_async
def get_menu(menu_id):
    return Menu.objects.get(id=menu_id)