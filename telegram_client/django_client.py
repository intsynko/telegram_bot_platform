import os
import sys
import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.scenarios.models import Scenario



@sync_to_async
def get_first_scenario():
    return Scenario.objects.first()

@sync_to_async
def get_scenario_by_id(scenario_id):
    return Scenario.objects.get(id=scenario_id)
