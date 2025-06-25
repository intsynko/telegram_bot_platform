from rest_framework import serializers
from apps.scenarios.models import Scenario, ScenarioElement
from apps.forms.models import Form, FormField
from apps.menu.models import Menu, MenuField


class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'name']


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'name', 'field_type', 'hidden', 'default_value', 'required']


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ['id', 'name', 'final_message', 'fields']

    fields = FormFieldSerializer(many=True)


class MenuFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuField
        fields = ['id', 'name', 'field_type', 'show_condition', 'linked_element']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'fields']

    fields = MenuFieldSerializer(many=True)


class ScenarioElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioElement
        fields = ['id', 'action_type', 'form', 'menu', 'order']

    form = FormSerializer()
    menu = MenuSerializer()


class ScenarioDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'name', 'elements']

    elements = ScenarioElementSerializer(many=True)
