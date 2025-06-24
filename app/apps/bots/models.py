from django.db import models


class Bot(models.Model):
    token = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bots')
    scenario = models.ForeignKey('scenarios.Scenario', null=True, blank=True, on_delete=models.SET_NULL, related_name='bots')

    def __str__(self):
        return self.name
