from django.db import models


class Scenario(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='scenatios', null=True)
    graph = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class ScenarioElement(models.Model):
    ACTION_TYPES = [
        ('form', 'Форма'),
        ('menu', 'Меню'),
        ('break', 'Выход из диалога'),
    ]
    scenario = models.ForeignKey(Scenario, related_name='elements', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    form = models.ForeignKey('forms.Form', null=True, blank=True, on_delete=models.SET_NULL)
    menu = models.ForeignKey('menu.Menu', null=True, blank=True, on_delete=models.SET_NULL)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_action_type_display()} (#{self.order})"
