from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

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

    @action(methods=["post"], detail=True)
    def run(self, request: Request, **kwargs) -> Response:
        """
        Run bot
        """
        bot = self.get_object()
        # bot.is_running = True
        # bot.save()
        return Response({"success": True})

    @action(methods=["post"], detail=True)
    def stop(self, request: Request, **kwargs) -> Response:
        """
        Stop bot
        """
        bot = self.get_object()
        # bot.is_running = False
        # bot.save()
        return Response({"success": True})
