from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('', views.ChatListByBotView.as_view(), name='chat-list'),
    path('by_bot/<int:bot_id>/', views.get_bot_chats_paginated, name='bot-chats-paginated'),
    path('<int:chat_id>/form-fields/', views.get_chat_form_fields, name='chat-form-fields'),
]
