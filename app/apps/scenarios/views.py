from rest_framework import viewsets, permissions
from .models import Scenario
from .serializers import ScenarioSerializer, ScenarioDetailSerializer


class ScenariosViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Scenario.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ScenarioDetailSerializer
        elif self.action in ['list', 'delete', 'create']:
            return ScenarioSerializer
        else:
            raise NotImplementedError

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
