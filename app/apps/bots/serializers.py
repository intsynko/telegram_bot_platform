from rest_framework import serializers

from apps.bots.bot_manager import is_bot_running
from apps.bots.models import Bot
from apps.scenarios.models import Scenario


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'name']


class BotReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'name', 'token', 'scenario', 'is_running']

    scenario = ScenarioSerializer()
    is_running = serializers.SerializerMethodField()

    def get_is_running(self, obj: Bot):
        return is_bot_running(obj.id)


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'name', 'token', 'scenario']


class BotSetScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['scenario']