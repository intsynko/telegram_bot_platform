from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.bots.models import Bot
from apps.bots.serializers import BotSerializer, BotReadSerializer, \
    BotSetScenarioSerializer
from apps.bots.logic import facades, selectors


class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return selectors.get_user_bots(self.request.user)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BotReadSerializer
        else:
            return BotSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=["post"], detail=True)
    def run(self, request: Request, **kwargs) -> Response:
        """Запуск бота"""
        bot = self.get_object()
        if not facades.validate_bot_scenario(bot):
            return Response(
                {"error": "No scenario selected"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        started = facades.start_bot_instance(bot.id)
        return Response({"success": started})

    @action(methods=["post"], detail=True)
    def stop(self, request: Request, **kwargs) -> Response:
        """Остановка бота"""
        bot = self.get_object()
        stopped = facades.stop_bot_instance(bot.id)
        return Response({"success": stopped})

    @action(methods=["post"], detail=True)
    def set_scenario(self, request: Request, **kwargs) -> Response:
        """Привязка сценария к боту"""
        bot = self.get_object()
        serializer = BotSetScenarioSerializer(instance=bot, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        scenario = serializer.validated_data['scenario']
        updated_bot = facades.assign_scenario_to_bot(bot, scenario)
        
        return Response(BotReadSerializer(instance=updated_bot).data)
