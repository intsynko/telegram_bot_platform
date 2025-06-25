from rest_framework import serializers
from .models import Bot
from ..scenarios.models import Scenario


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'name']


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = ['id', 'name', 'token', 'scenario']

    scenario = ScenarioSerializer()
