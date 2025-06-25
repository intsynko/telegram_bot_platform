from rest_framework.routers import DefaultRouter
from .views import BotViewSet

router = DefaultRouter()
router.register(r'', BotViewSet, basename='bot')

urlpatterns = router.urls
