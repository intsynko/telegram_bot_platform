"""
Тесты для адаптеров
"""
import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from telegram_client.adapters import (
    TelegramBotAdapter, DjangoAdapter, BotAdapter,
    TelegramNotificationAdapter, EmailNotificationAdapter,
    create_bot_adapter
)
from .mocks import MockUpdate, MockTelegramAdapter, MockDatabaseAdapter, MockNotificationAdapter


class TestTelegramBotAdapter(unittest.TestCase):
    """Тесты для TelegramBotAdapter"""
    
    def setUp(self):
        """Настройка тестов"""
        self.adapter = TelegramBotAdapter()
        self.update = MockUpdate("Hello world", 123, 456, "testuser")
    
    async def test_send_text_message(self):
        """Тест отправки текстового сообщения"""
        # Выполнение
        await self.adapter.send_text_message(self.update, "Test message")
        
        # Проверки
        self.update.message.reply_text.assert_called_once_with("Test message")
    
    async def test_send_menu_message(self):
        """Тест отправки сообщения с меню"""
        # Подготовка
        buttons = [{"label": "Option 1"}, {"label": "Option 2"}]
        
        # Выполнение
        await self.adapter.send_menu_message(self.update, "Choose:", buttons)
        
        # Проверки
        self.update.message.reply_text.assert_called_once()
        args, kwargs = self.update.message.reply_text.call_args
        self.assertEqual(args[0], "Choose:")
        self.assertIn('reply_markup', kwargs)
    
    def test_get_user_id(self):
        """Тест получения ID пользователя"""
        result = self.adapter.get_user_id(self.update)
        self.assertEqual(result, 123)
    
    def test_get_chat_id(self):
        """Тест получения ID чата"""
        result = self.adapter.get_chat_id(self.update)
        self.assertEqual(result, 456)
    
    def test_get_username(self):
        """Тест получения имени пользователя"""
        result = self.adapter.get_username(self.update)
        self.assertEqual(result, "testuser")
    
    def test_get_message_text(self):
        """Тест получения текста сообщения"""
        result = self.adapter.get_message_text(self.update)
        self.assertEqual(result, "Hello world")
    
    def test_get_message_text_no_message(self):
        """Тест получения текста сообщения когда сообщения нет"""
        self.update.message = None
        result = self.adapter.get_message_text(self.update)
        self.assertIsNone(result)


class TestDjangoAdapter(unittest.TestCase):
    """Тесты для DjangoAdapter"""
    
    def setUp(self):
        """Настройка тестов"""
        self.adapter = DjangoAdapter()
    
    async def test_save_message(self):
        """Тест сохранения сообщения"""
        with patch.object(self.adapter, 'django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            # Выполнение
            await self.adapter.save_message(123, "Test message", True)
            
            # Проверки
            mock_client.create_message.assert_called_once_with(123, "Test message", True)
    
    async def test_get_or_create_chat(self):
        """Тест получения или создания чата"""
        with patch.object(self.adapter, 'django_client') as mock_client:
            mock_client.get_or_create_chat = AsyncMock(return_value=("chat_obj", True))
            
            # Выполнение
            result = await self.adapter.get_or_create_chat(123, 456, 1, "testuser", {"key": "value"})
            
            # Проверки
            self.assertEqual(result, ("chat_obj", True))
            mock_client.get_or_create_chat.assert_called_once_with(
                telegram_user_id=123,
                telegram_username="testuser",
                telegram_chat_id=456,
                bot_id=1,
                context={"key": "value"}
            )


class TestBotAdapter(unittest.TestCase):
    """Тесты для главного адаптера бота"""
    
    def setUp(self):
        """Настройка тестов"""
        self.telegram_adapter = MockTelegramAdapter()
        self.database_adapter = MockDatabaseAdapter()
        self.notification_adapters = {
            'telegram': MockNotificationAdapter(),
            'email': MockNotificationAdapter()
        }
        
        self.bot_adapter = BotAdapter(
            self.telegram_adapter,
            self.database_adapter,
            self.notification_adapters
        )
        
        self.update = MockUpdate()
    
    async def test_send_message(self):
        """Тест отправки сообщения"""
        # Выполнение
        await self.bot_adapter.send_message(self.update, "Test message")
        
        # Проверки
        self.telegram_adapter.send_text_message.assert_called_once_with(self.update, "Test message")
    
    async def test_send_menu(self):
        """Тест отправки меню"""
        # Подготовка
        buttons = [{"label": "Option 1"}]
        
        # Выполнение
        await self.bot_adapter.send_menu(self.update, "Choose:", buttons)
        
        # Проверки
        self.telegram_adapter.send_menu_message.assert_called_once_with(self.update, "Choose:", buttons)
    
    async def test_save_message(self):
        """Тест сохранения сообщения"""
        # Выполнение
        await self.bot_adapter.save_message(123, "Test message", True)
        
        # Проверки
        self.database_adapter.save_message.assert_called_once_with(123, "Test message", True)
    
    def test_send_notification_telegram(self):
        """Тест отправки Telegram уведомления"""
        # Выполнение
        self.bot_adapter.send_notification("Test notification", "telegram", "123456")
        
        # Проверки
        self.notification_adapters['telegram'].send_notification.assert_called_once_with(
            "Test notification", "123456"
        )
    
    def test_send_notification_unknown_type(self):
        """Тест отправки уведомления неизвестного типа"""
        with patch('telegram_client.adapters.logger') as mock_logger:
            # Выполнение
            self.bot_adapter.send_notification("Test", "unknown_type")
            
            # Проверки
            mock_logger.warning.assert_called_once_with("Неизвестный тип уведомления: unknown_type")
    
    def test_get_user_data(self):
        """Тест получения данных пользователя"""
        # Выполнение
        result = self.bot_adapter.get_user_data(self.update)
        
        # Проверки
        expected = {
            'user_id': 123,
            'chat_id': 456,
            'username': 'testuser',
            'message_text': 'test message'
        }
        self.assertEqual(result, expected)


class TestNotificationAdapters(unittest.TestCase):
    """Тесты для адаптеров уведомлений"""
    
    def test_telegram_notification_adapter_with_token(self):
        """Тест Telegram адаптера с токеном"""
        adapter = TelegramNotificationAdapter("test_token")
        
        with patch('telegram_client.utils.TelegramConnector') as mock_connector_class:
            mock_connector = Mock()
            mock_connector_class.return_value = mock_connector
            
            # Выполнение
            adapter.send_notification("Test message", "123456")
            
            # Проверки
            mock_connector_class.assert_called_once_with("test_token", "123456")
            mock_connector.send_message.assert_called_once_with("Test message")
    
    def test_telegram_notification_adapter_no_token(self):
        """Тест Telegram адаптера без токена"""
        adapter = TelegramNotificationAdapter(None)
        
        with patch('telegram_client.adapters.logger') as mock_logger:
            # Выполнение
            adapter.send_notification("Test message")
            
            # Проверки
            mock_logger.info.assert_called_once_with(
                "Уведомление (не отправлено, нет токена): Test message"
            )
    
    def test_email_notification_adapter(self):
        """Тест Email адаптера"""
        adapter = EmailNotificationAdapter()
        
        with patch('telegram_client.adapters.logger') as mock_logger:
            # Выполнение
            adapter.send_notification("Test email")
            
            # Проверки
            mock_logger.info.assert_called_once_with("Email уведомление: Test email")


class TestCreateBotAdapter(unittest.TestCase):
    """Тесты для фабрики создания адаптера"""
    
    def test_create_bot_adapter_with_token(self):
        """Тест создания адаптера с токеном"""
        # Выполнение
        adapter = create_bot_adapter("test_token")
        
        # Проверки
        self.assertIsInstance(adapter, BotAdapter)
        self.assertIn('telegram', adapter.notifications)
        self.assertIn('email', adapter.notifications)
    
    def test_create_bot_adapter_without_token(self):
        """Тест создания адаптера без токена"""
        # Выполнение
        adapter = create_bot_adapter(None)
        
        # Проверки
        self.assertIsInstance(adapter, BotAdapter)
        self.assertNotIn('telegram', adapter.notifications)
        self.assertIn('email', adapter.notifications)


def run_async_test(coro):
    """Хелпер для запуска асинхронных тестов"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Преобразуем асинхронные тесты в синхронные
test_classes = [TestTelegramBotAdapter, TestDjangoAdapter, TestBotAdapter]

for test_class in test_classes:
    for name in dir(test_class):
        if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_class, name)):
            test_method = getattr(test_class, name)
            setattr(test_class, name, lambda self, method=test_method: run_async_test(method(self)))


if __name__ == '__main__':
    unittest.main()
