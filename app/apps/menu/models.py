from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class MenuField(models.Model):
    SCENARIO_ELEMENT_LINK = 'scenario_element_link'
    EXIT = 'exit'
    FIELD_TYPES = [
        (SCENARIO_ELEMENT_LINK, 'Ссылка на элемент сценарий'),
        (EXIT, 'Выход'),
    ]
    menu = models.ForeignKey(Menu, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=55, choices=FIELD_TYPES)
    show_condition = models.CharField(max_length=1000, null=True, blank=True)
    linked_element = models.ForeignKey('scenarios.ScenarioElement', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.name} {self.field_type}"
