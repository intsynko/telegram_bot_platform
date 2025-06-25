from rest_framework.routers import DefaultRouter
from apps.scenarios.views import ScenariosViewSet

router = DefaultRouter()
router.register(r'', ScenariosViewSet, basename='scenarios')

urlpatterns = router.urls
