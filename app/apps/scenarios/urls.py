from rest_framework.routers import DefaultRouter
from apps.scenarios.views import ScenariosViewSet, ScenariosExampleViewSet

router = DefaultRouter()
router.register('template', ScenariosExampleViewSet, basename='scenarios-template')
router.register(r'', ScenariosViewSet, basename='scenarios')


urlpatterns = router.urls
