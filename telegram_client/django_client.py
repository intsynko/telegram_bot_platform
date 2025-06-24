import os
import sys
import django
from asgiref.sync import sync_to_async


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.scenarios.models import Scenario, ScenarioElement
from apps.forms.models import Form, FormField


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
def get_fields_for_form(form_id):
    return list(FormField.objects.filter(form_id=form_id))