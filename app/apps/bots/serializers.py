from rest_framework import serializers
from .models import Bot
from ..scenarios.models import Scenario


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
        return False


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'name', 'token', 'scenario']
