from django.contrib import admin
from .models import Scenario, ScenarioElement

class ScenarioElementInline(admin.TabularInline):
    model = ScenarioElement
    extra = 1

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    inlines = [ScenarioElementInline]
    list_display = ('id', 'name')

@admin.register(ScenarioElement)
class ScenarioElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'scenario', 'action_type', 'form', 'order')
    list_filter = ('scenario', 'action_type')
