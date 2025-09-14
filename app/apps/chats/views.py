from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import Chat, FormField
from .serializers import ChatSerializer, FormFieldSerializer
from apps.bots.models import Bot


class ChatListByBotView(generics.ListAPIView):
    serializer_class = ChatSerializer
    
    def get_queryset(self):
        bot_id = self.kwargs['bot_id']
        return Chat.objects.filter(bot_id=bot_id).prefetch_related('form_fields', 'messages').order_by('-created_at')


@api_view(['GET'])
def get_bot_chats_paginated(request, bot_id):
    """Получить чаты бота с пагинацией"""
    try:
        # Проверяем, что бот существует
        bot = Bot.objects.get(id=bot_id)
    except Bot.DoesNotExist:
        return Response({'error': 'Бот не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    # Получаем параметры пагинации
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Получаем чаты с связанными данными
    chats = Chat.objects.filter(bot_id=bot_id).prefetch_related('form_fields', 'messages').order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(chats, page_size)
    page_obj = paginator.get_page(page)
    
    # Сериализация
    serializer = ChatSerializer(page_obj.object_list, many=True)
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })


@api_view(['GET'])
def get_chat_form_fields(request, chat_id):
    """Получить поля формы для конкретного чата"""
    try:
        chat = Chat.objects.get(id=chat_id)
        form_fields = FormField.objects.filter(chat=chat).order_by('created_at')
        serializer = FormFieldSerializer(form_fields, many=True)
        return Response(serializer.data)
    except Chat.DoesNotExist:
        return Response({'error': 'Чат не найден'}, status=status.HTTP_404_NOT_FOUND)
