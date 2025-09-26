from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ChatPagination(PageNumberPagination):
    """Пагинация для чатов согласно правилам"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        """Кастомный формат ответа с динамическими полями форм"""
        # Получаем уникальные поля форм из контекста
        form_fields = getattr(self, 'form_fields', [])
        
        return Response({
            'results': data,
            'form_fields': form_fields,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
            'next': self.get_next_link(),
            'previous': self.get_previous_link()
        })
