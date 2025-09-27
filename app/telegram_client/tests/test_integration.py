"""
Интеграционные тесты для telegram_client
Фиксируют текущую логику работы перед рефакторингом
"""
import os
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from apps.bots.models import Bot
from apps.scenarios.models import Scenario
from apps.chats.models import Chat, Message, FormField
from telegram_client.app import start, run_scenario, restore_chat_context
from telegram_client import django_client

User = get_user_model()


class TelegramIntegrationTestCase(TestCase):
    """Интеграционные тесты для telegram_client"""

    def setUp(self):
        """Настройка тестовых данных"""
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем бота
        self.bot = Bot.objects.create(
            name='Test Bot',
            token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
            owner=self.user,
            description='Test bot for integration tests'
        )
        
        # Создаем простой сценарий
        self.scenario = Scenario.objects.create(
            name='Test Scenario',
            owner=self.user,
            graph={
                "nodes": [
                    {
                        "id": "start",
                        "type": "message",
                        "data": {"text": "Привет! Как дела?"}
                    },
                    {
                        "id": "form1",
                        "type": "form",
                        "data": {
                            "question": "Как вас зовут?",
                            "field": "name"
                        }
                    },
                    {
                        "id": "end",
                        "type": "message",
                        "data": {"text": "Спасибо, {name}!"}
                    }
                ],
                "edges": [
                    {"source": "start", "target": "form1"},
                    {"source": "form1", "target": "end"}
                ]
            }
        )
        
        # Привязываем сценарий к боту
        self.bot.scenario = self.scenario
        self.bot.save()
        
        # Тестовые данные Telegram
        self.telegram_user_id = 123456789
        self.telegram_username = 'testuser'
        self.telegram_chat_id = 987654321

    def create_mock_update(self, text="/start", is_start=True):
        """Создает мок объект Update для тестирования"""
        update = Mock()
        update.effective_user = Mock()
        update.effective_user.id = self.telegram_user_id
        update.effective_user.username = self.telegram_username
        update.effective_chat = Mock()
        update.effective_chat.id = self.telegram_chat_id
        update.message = Mock()
        update.message.text = text
        update.message.reply_text = AsyncMock()
        return update

    def create_mock_context(self, user_data=None):
        """Создает мок объект ContextTypes.DEFAULT_TYPE"""
        context = Mock()
        context.user_data = user_data or {}
        return context

    def test_start_command_creates_new_chat(self):
        """Тест: команда /start создает новый чат в БД"""
        # Arrange
        update = self.create_mock_update("/start")
        context = self.create_mock_context()
        
        # Убеждаемся что чата еще нет
        self.assertFalse(
            Chat.objects.filter(
                telegram_chat_id=self.telegram_chat_id,
                bot=self.bot
            ).exists()
        )
        
        # Act
        with patch.dict(os.environ, {'BOT_ID': str(self.bot.id)}):
            result = asyncio.run(start(update, context))
        
        # Assert
        # Проверяем что чат создался
        chat = Chat.objects.get(
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot
        )
        self.assertEqual(chat.telegram_user_id, self.telegram_user_id)
        self.assertEqual(chat.telegram_username, self.telegram_username)
        
        # Проверяем что сообщение сохранилось
        message = Message.objects.get(chat=chat, text="/start")
        self.assertTrue(message.is_user_message)
        
        # Проверяем что контекст обновился
        self.assertEqual(context.user_data['chat_id'], chat.id)

    def test_start_command_restores_existing_chat(self):
        """Тест: команда /start восстанавливает существующий чат"""
        # Arrange - создаем существующий чат
        existing_chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context={'existing': 'data'}
        )
        
        update = self.create_mock_update("/start")
        context = self.create_mock_context()
        
        # Act
        with patch.dict(os.environ, {'BOT_ID': str(self.bot.id)}):
            result = asyncio.run(start(update, context))
        
        # Assert
        # Проверяем что новый чат не создался
        chat_count = Chat.objects.filter(
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot
        ).count()
        self.assertEqual(chat_count, 1)
        
        # Проверяем что контекст восстановился
        self.assertEqual(context.user_data['chat_id'], existing_chat.id)

    def test_text_message_processing(self):
        """Тест: обработка текстового сообщения сохраняется в БД"""
        # Arrange
        chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context={}
        )
        
        update = self.create_mock_update("Привет, бот!")
        context = self.create_mock_context({'chat_id': chat.id})
        
        # Act
        with patch.dict(os.environ, {'BOT_ID': str(self.bot.id)}):
            result = asyncio.run(run_scenario(update, context))
        
        # Assert
        # Проверяем что сообщение сохранилось
        message = Message.objects.get(
            chat=chat,
            text="Привет, бот!",
            is_user_message=True
        )
        self.assertIsNotNone(message)

    def test_scenario_execution_flow(self):
        """Тест: выполнение простого сценария с сохранением контекста"""
        # Arrange
        chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context={}
        )
        
        update = self.create_mock_update("Начать")
        context = self.create_mock_context({
            'chat_id': chat.id,
            'scenario_id': self.scenario.id,
            'graph': self.scenario.graph
        })
        
        # Act
        with patch.dict(os.environ, {'BOT_ID': str(self.bot.id)}):
            result = asyncio.run(run_scenario(update, context))
        
        # Assert
        # Проверяем что контекст обновился в БД
        chat.refresh_from_db()
        self.assertIsNotNone(chat.context)

    def test_restore_chat_context_existing_chat(self):
        """Тест: восстановление контекста существующего чата"""
        # Arrange
        existing_context = {
            'scenario_id': self.scenario.id,
            'node': 'form1',
            'answers': {'name': 'Тест'}
        }
        chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context=existing_context
        )
        
        context = self.create_mock_context()
        
        # Act
        result = asyncio.run(restore_chat_context(
            self.telegram_chat_id,
            self.bot.id,
            context
        ))
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(context.user_data['chat_id'], chat.id)
        self.assertEqual(context.user_data['context'], existing_context)

    def test_restore_chat_context_nonexistent_chat(self):
        """Тест: восстановление контекста несуществующего чата"""
        # Arrange
        context = self.create_mock_context()
        nonexistent_chat_id = 999999999
        
        # Act
        result = asyncio.run(restore_chat_context(
            nonexistent_chat_id,
            self.bot.id,
            context
        ))
        
        # Assert
        self.assertFalse(result)
        self.assertEqual(context.user_data, {})

    def test_form_field_saving(self):
        """Тест: сохранение ответов в поля формы"""
        # Arrange
        chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context={}
        )
        
        # Act
        asyncio.run(django_client.save_or_update_form_field(
            chat.id,
            'name',
            'Иван Петров'
        ))
        
        # Assert
        form_field = FormField.objects.get(chat=chat, name='name')
        self.assertEqual(form_field.value, 'Иван Петров')

    def test_chat_context_update(self):
        """Тест: обновление контекста чата"""
        # Arrange
        chat = Chat.objects.create(
            telegram_user_id=self.telegram_user_id,
            telegram_username=self.telegram_username,
            telegram_chat_id=self.telegram_chat_id,
            bot=self.bot,
            context={'old': 'data'}
        )
        
        new_context = {'new': 'data', 'scenario_id': self.scenario.id}
        
        # Act
        asyncio.run(django_client.update_chat_context(chat.id, new_context))
        
        # Assert
        chat.refresh_from_db()
        self.assertEqual(chat.context, new_context)

    def tearDown(self):
        """Очистка после тестов"""
        # Django автоматически очищает тестовую БД
        pass
