from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Scenario
from .serializers import ScenarioSerializer, ScenarioDetailSerializer
from .logic import facades, selectors


class ScenariosViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'copy':
            return selectors.get_template_scenarios()
        else:
            return selectors.get_user_scenarios(self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ScenarioDetailSerializer
        elif self.action in ['list', 'delete', 'create']:
            return ScenarioSerializer
        else:
            raise NotImplementedError

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def copy(self, request, pk: int):
        """Копирование шаблонного сценария"""
        try:
            new_scenario = facades.copy_template_scenario(pk, request.user)
            serializer = ScenarioDetailSerializer(instance=new_scenario)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except ValueError:
            raise NotFound("Template scenario not found")


class ScenariosExampleViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return selectors.get_template_scenarios()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return ScenarioDetailSerializer
        elif self.action in ['list']:
            return ScenarioSerializer
        else:
            raise NotImplementedError

