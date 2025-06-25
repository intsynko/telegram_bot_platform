from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Bot
from .serializers import BotSerializer

# Create your views here.

class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
