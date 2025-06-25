from django.contrib import admin
from .models import Scenario


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
