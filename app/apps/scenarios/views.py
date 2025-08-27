from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Scenario
from .serializers import ScenarioSerializer, ScenarioDetailSerializer


class ScenariosViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Scenario.objects.all()
        if self.action == 'copy':
            qs = qs.filter(is_template=True)
        else:
            qs = qs.filter(owner=self.request.user)
        return qs
        # return Scenario.objects.filter(owner=self.request.user, is_template=False)

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
        user = self.get_object()
        scenario = Scenario.objects.filter(pk=pk, is_template=True).first()
        if scenario is None:
            raise NotFound()
        new_scenario = Scenario.objects.create(
            graph=scenario.graph,
            name=f"{scenario.name} - Копия",
            owner=request.user,
        )
        serializer = ScenarioDetailSerializer(instance=new_scenario)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ScenariosExampleViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = ScenarioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Scenario.objects.filter(is_template=True)

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return ScenarioDetailSerializer
        elif self.action in ['list']:
            return ScenarioSerializer
        else:
            raise NotImplementedError

