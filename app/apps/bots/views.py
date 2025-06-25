from rest_framework import viewsets, permissions
from apps.bots.models import Bot
from apps.bots.serializers import BotSerializer, BotReadSerializer


class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bot.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BotReadSerializer
        else:
            return BotSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
