from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet

from apps.chats.models import Chat, Message, FormField
from apps.chats.serializers import ChatSerializer, FormFieldSerializer, MessageSerializer, ChatWithDynamicFieldsSerializer
from apps.chats.pagination import ChatPagination
from apps.chats.logic import facades, selectors


class BotChatViewSet(mixins.ListModelMixin, GenericViewSet):
    """ViewSet для получения чатов конкретного бота с стандартной DRF пагинацией"""
    serializer_class = ChatWithDynamicFieldsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ChatPagination
    
    def get_queryset(self):
        """Используем селекторы согласно правилам"""
        bot_id = self.kwargs.get('bot_id')
        if bot_id:
            return selectors.get_bot_chats_queryset(bot_id)
        return Chat.objects.none()
    
    def get_serializer_context(self):
        """Добавляем уникальные поля форм в контекст сериализатора"""
        context = super().get_serializer_context()
        bot_id = self.kwargs.get('bot_id')
        if bot_id:
            form_field_names = selectors.get_unique_form_field_names(bot_id)
            context['form_field_names'] = form_field_names
            # Добавляем в пагинатор для кастомного ответа
            if hasattr(self, 'paginator') and self.paginator:
                self.paginator.form_fields = form_field_names
        return context
    


class ChatViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """ViewSet для работы с отдельными чатами (без пагинации)"""
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Используем селекторы согласно правилам"""
        return Chat.objects.prefetch_related('form_fields', 'messages').order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def form_fields(self, request: Request, pk=None) -> Response:
        """Получить поля формы для конкретного чата (без пагинации)"""
        chat = self.get_object()
        form_fields = selectors.get_chat_form_fields(chat.id)
        serializer = FormFieldSerializer(form_fields, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request: Request, pk=None) -> Response:
        """Получить сообщения чата (без пагинации)"""
        chat = self.get_object()
        messages = selectors.get_chat_messages(chat.id)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)