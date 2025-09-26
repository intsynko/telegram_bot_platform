from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.chats.views import ChatViewSet, BotChatViewSet

# Создаем роутер для стандартных операций с чатами
router = DefaultRouter()
router.register(r'', ChatViewSet, basename='chat')

# URL patterns с правильным разделением ответственности
urlpatterns = [
    # Отдельный ViewSet для пагинированных чатов бота (согласно правилам)
    path('by_bot/<int:bot_id>/', BotChatViewSet.as_view({'get': 'list'}), name='chats-by-bot'),
    
    # Оригинальный формат для form-fields и messages (actions без пагинации)
    path('<int:pk>/form-fields/', ChatViewSet.as_view({'get': 'form_fields'}), name='chat-form-fields'),
    path('<int:pk>/messages/', ChatViewSet.as_view({'get': 'messages'}), name='chat-messages'),
    
    # Включаем стандартные роуты для отдельных чатов
    path('', include(router.urls)),
]