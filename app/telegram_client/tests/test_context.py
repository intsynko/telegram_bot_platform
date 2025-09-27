"""
Тесты для функций управления контекстом
"""
import unittest
from unittest.mock import patch, AsyncMock, Mock
import asyncio

from telegram_client.context import (
    save_user_message, get_current_node, restore_chat_context,
    save_answers_to_form_fields, ensure_chat_exists, ensure_scenario_initialized,
    ensure_node_initialized, save_context_to_database, save_bot_message
)
from .mocks import MockUpdate, MockContext, create_mock_context_with_scenario


class TestContextFunctions(unittest.TestCase):
    """Тесты для функций управления контекстом"""
    
    def setUp(self):
        """Настройка тестов"""
        self.update = MockUpdate("Hello world", 123, 456, "testuser")
        self.context = create_mock_context_with_scenario()
    
    async def test_save_user_message(self):
        """Тест сохранения сообщения пользователя"""
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            
            # Выполнение
            await save_user_message(self.update, self.context)
            
            # Проверки
            mock_client.create_message.assert_called_once_with(
                chat_id=789,
                text="Hello world",
                is_user_message=True
            )
    
    async def test_save_user_message_exclude_commands(self):
        """Тест сохранения сообщения пользователя (исключение команд)"""
        self.update.message.text = "/start"
        
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            
            # Выполнение
            await save_user_message(self.update, self.context, exclude_commands=True)
            
            # Проверки
            mock_client.create_message.assert_not_called()
    
    async def test_save_user_message_no_chat_id(self):
        """Тест сохранения сообщения без chat_id"""
        # Создаем контекст без chat_id
        context_without_chat = MockContext({'answers': {}})
        
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            
            # Выполнение - ожидаем KeyError, так как функция не проверяет наличие chat_id
            with self.assertRaises(KeyError):
                await save_user_message(self.update, context_without_chat)
    
    def test_get_current_node(self):
        """Тест получения текущего узла"""
        # Подготовка
        self.context.user_data['graph'] = {
            'nodes': [
                {'id': 'node1', 'type': 'message'},
                {'id': 'node2', 'type': 'condition'}
            ]
        }
        self.context.user_data['node'] = 'node2'
        
        # Выполнение
        result = get_current_node(self.context)
        
        # Проверки
        self.assertEqual(result, {'id': 'node2', 'type': 'condition'})
    
    def test_get_current_node_not_found(self):
        """Тест получения несуществующего узла"""
        # Подготовка
        self.context.user_data['graph'] = {'nodes': []}
        self.context.user_data['node'] = 'nonexistent'
        
        # Выполнение
        result = get_current_node(self.context)
        
        # Проверки
        self.assertIsNone(result)
    
    async def test_restore_chat_context_success(self):
        """Тест успешного восстановления контекста чата"""
        chat_data = {
            'chat_id': 789,
            'context': {
                'scenario_id': 1,
                'node': 'current_node',
                'answers': {'name': 'John'}
            },
            'telegram_user_id': 123,
            'telegram_username': 'testuser'
        }
        
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.get_chat_context = AsyncMock(return_value=chat_data)
            
            # Мокируем get_scenario_by_id для восстановления graph
            mock_scenario = Mock()
            mock_scenario.graph = '{"nodes": [], "edges": []}'
            mock_client.get_scenario_by_id = AsyncMock(return_value=mock_scenario)
            
            # Мокируем get_chat_form_fields
            mock_client.get_chat_form_fields = AsyncMock(return_value={})
            
            # Выполнение
            result = await restore_chat_context(456, 1, self.context)  # bot_id должен быть int
            
            # Проверки
            self.assertTrue(result)
            self.assertEqual(self.context.user_data['chat_id'], 789)
            self.assertEqual(self.context.user_data['scenario_id'], 1)
            self.assertEqual(self.context.user_data['node'], 'current_node')
            self.assertEqual(self.context.user_data['answers'], {'name': 'John'})
    
    async def test_restore_chat_context_no_data(self):
        """Тест восстановления контекста когда данных нет"""
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.get_chat_context = AsyncMock(return_value=None)
            
            # Выполнение
            result = await restore_chat_context(456, 1, self.context)  # bot_id должен быть int
            
            # Проверки
            self.assertFalse(result)
    
    async def test_save_answers_to_form_fields(self):
        """Тест сохранения ответов в поля формы"""
        answers = {
            'name': 'John',
            'email': 'john@example.com'
        }
        
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.save_or_update_form_field = AsyncMock()
            
            # Выполнение
            await save_answers_to_form_fields(789, answers)
            
            # Проверки
            # Проверяем, что функция была вызвана правильное количество раз
            self.assertEqual(mock_client.save_or_update_form_field.call_count, 2)
            
            # Проверяем конкретные вызовы
            calls = mock_client.save_or_update_form_field.call_args_list
            call_args = [call[0] for call in calls]
            
            # Проверяем, что все ожидаемые вызовы присутствуют
            expected_args = [
                (789, 'name', 'John'),
                (789, 'email', 'john@example.com')
            ]
            
            for expected in expected_args:
                self.assertIn(expected, call_args)
    
    async def test_ensure_chat_exists_simple(self):
        """Тест обеспечения существования чата (упрощенный)"""
        # Просто проверяем, что функция не падает
        with patch('telegram_client.context.restore_chat_context', new_callable=AsyncMock) as mock_restore, \
             patch('telegram_client.context.django_client') as mock_client, \
             patch.dict('os.environ', {'BOT_ID': '1'}):
            
            mock_restore.return_value = False
            mock_client.get_or_create_chat = AsyncMock(return_value=(Mock(id=789), True))
            
            # Выполнение
            await ensure_chat_exists(self.update, self.context)
            
            # Проверки
            self.assertEqual(self.context.user_data['chat_id'], 789)
    
    async def test_ensure_scenario_initialized_no_scenario(self):
        """Тест инициализации сценария (сценарий отсутствует)"""
        # Убеждаемся, что scenario_id НЕ установлен
        self.context.user_data.pop('scenario_id', None)
        # Добавляем chat_id в контекст для save_bot_message
        self.context.user_data['chat_id'] = 789
        
        with patch('telegram_client.context.django_client') as mock_client, \
             patch('telegram_client.context.save_bot_message', new_callable=AsyncMock) as mock_save_bot, \
             patch.dict('os.environ', {'BOT_ID': '1'}):
            
            mock_client.get_scenario_by_bot = AsyncMock(return_value=None)
            
            # Выполнение
            result = await ensure_scenario_initialized(self.update, self.context)
            
            # Проверки
            self.update.message.reply_text.assert_called_once_with('Нет доступных сценариев.')
            mock_save_bot.assert_called_once_with(789, 'Нет доступных сценариев.')
            # Функция должна вернуть ConversationHandler.END
            self.assertIsNotNone(result)
    
    async def test_ensure_scenario_initialized_success(self):
        """Тест успешной инициализации сценария"""
        mock_scenario = Mock()
        mock_scenario.id = 1
        mock_scenario.graph = '{"nodes": [], "edges": []}'
        
        with patch('telegram_client.context.django_client') as mock_client, \
             patch.dict('os.environ', {'BOT_ID': '1'}):
            
            mock_client.get_scenario_by_bot = AsyncMock(return_value=mock_scenario)
            
            # Выполнение
            result = await ensure_scenario_initialized(self.update, self.context)
            
            # Проверки
            self.assertIsNone(result)  # Успешная инициализация
            self.assertEqual(self.context.user_data['scenario_id'], 1)
            self.assertEqual(self.context.user_data['graph'], {"nodes": [], "edges": []})
            self.assertEqual(self.context.user_data['answers'], {})
    
    async def test_ensure_node_initialized(self):
        """Тест инициализации узла"""
        self.context.user_data['graph'] = {'nodes': [{'id': 'start_node', 'type': 'start'}]}
        
        # Выполнение (без узла)
        await ensure_node_initialized(self.context)
        
        # Проверки - узел должен быть установлен
        self.assertIsNotNone(self.context.user_data.get('node'))
    
    async def test_save_context_to_database(self):
        """Тест сохранения контекста в базу данных"""
        self.context.user_data.update({
            'scenario_id': 1,
            'node': 'current_node',
            'answers': {'name': 'John'},
            'form': {'id': 'form1'},
            'fields': [{'name': 'field1'}],
            'field_idx': 0,
            'asked': True
        })
        
        with patch('telegram_client.context.django_client') as mock_client, \
             patch('telegram_client.context.save_answers_to_form_fields', new_callable=AsyncMock) as mock_save_answers:
            
            mock_client.update_chat_context = AsyncMock()
            
            # Выполнение
            await save_context_to_database(self.context)
            
            # Проверки
            expected_context = {
                'scenario_id': 1,
                'node': 'current_node',
                'answers': {'name': 'John'},
                'form': {'id': 'form1'},
                'fields': [{'name': 'field1'}],
                'field_idx': 0,
                'asked': True
            }
            mock_client.update_chat_context.assert_called_once_with(789, expected_context)
            mock_save_answers.assert_called_once_with(789, {'name': 'John'})
    
    async def test_save_bot_message(self):
        """Тест сохранения сообщения бота"""
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            
            # Выполнение
            await save_bot_message(789, "Bot message")
            
            # Проверки
            mock_client.create_message.assert_called_once_with(
                chat_id=789,
                text="Bot message",
                is_user_message=False
            )
    
    async def test_save_bot_message_no_chat_id(self):
        """Тест сохранения сообщения бота без chat_id"""
        with patch('telegram_client.context.django_client') as mock_client:
            mock_client.create_message = AsyncMock()
            
            # Выполнение
            await save_bot_message(None, "Bot message")
            
            # Проверки
            mock_client.create_message.assert_not_called()


def run_async_test(coro):
    """Хелпер для запуска асинхронных тестов"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Преобразуем асинхронные тесты в синхронные
for name in dir(TestContextFunctions):
    if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestContextFunctions, name)):
        test_method = getattr(TestContextFunctions, name)
        setattr(TestContextFunctions, name, lambda self, method=test_method: run_async_test(method(self)))


if __name__ == '__main__':
    unittest.main()
