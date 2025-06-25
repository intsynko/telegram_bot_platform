from django.db import models


class Scenario(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='scenatios', null=True)
    graph = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
