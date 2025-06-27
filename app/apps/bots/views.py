from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.bots.models import Bot
from apps.bots.serializers import BotSerializer, BotReadSerializer
from apps.bots.bot_manager import start_bot, stop_bot


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
        if not bot.scenario:
            return Response({"error": "No scenario selected"}, status=400)
        started = start_bot(bot.id)
        return Response({"success": started})

    @action(methods=["post"], detail=True)
    def stop(self, request: Request, **kwargs) -> Response:
        """
        Stop bot
        """
        bot = self.get_object()
        stopped = stop_bot(bot.id)
        return Response({"success": stopped})
