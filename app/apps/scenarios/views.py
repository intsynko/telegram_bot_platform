from rest_framework import viewsets, permissions
from .models import Scenario
from .serializers import ScenarioSerializer


class ScenariosViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Scenario.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
