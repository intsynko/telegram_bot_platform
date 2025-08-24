import os
import sys
import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+ '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from apps.scenarios.models import Scenario
from apps.bots.models import Bot


@sync_to_async
def get_scenario_by_bot(bot_id):
    return Scenario.objects.get(bots__id=bot_id)

def get_bot_by_id(bot_id):
    return Bot.objects.get(id=bot_id)

@sync_to_async
def get_scenario_by_id(scenario_id):
    return Scenario.objects.get(id=scenario_id)
