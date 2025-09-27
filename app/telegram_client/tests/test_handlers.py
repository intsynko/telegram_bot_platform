"""
Тесты для хендлеров узлов сценария
"""
import unittest
from unittest.mock import patch, AsyncMock, Mock
import asyncio

from telegram_client.handlers import (
    process_message_node, process_condition_node, process_notification_node,
    process_datawrite_node, process_form_node, process_menu_node, process_break_node,
    CONTINUE_SCENARIO, WAIT_USER_INPUT, END_CONVERSATION, move_to_next_node
)
from .mocks import (
    MockUpdate, MockContext, MockBotAdapter,
    create_message_node, create_condition_node, create_notification_node,
    create_datawrite_node, create_form_node, create_menu_node, create_break_node,
    create_mock_context_with_scenario, MockFormField
)


class TestHandlers(unittest.TestCase):
    """Тесты для хендлеров узлов сценария"""
    
    def setUp(self):
        """Настройка тестов"""
        self.update = MockUpdate()
        self.context = create_mock_context_with_scenario()
        self.bot_adapter = MockBotAdapter()
    
    async def test_process_message_node(self):
        """Тест обработки узла message"""
        # Подготовка
        node = create_message_node("Hello, {name}!")
        self.context.user_data['answers'] = {'name': 'John'}
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move, \
             patch('telegram_client.handlers.format_str', return_value="Hello, John!") as mock_format:
            # Выполнение
            result = await process_message_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            mock_format.assert_called_once_with("Hello, {name}!", {'name': 'John'})
            self.bot_adapter.send_message.assert_called_once_with(self.update, "Hello, John!")
            self.bot_adapter.save_message.assert_called_once_with(789, "Hello, John!", is_user=False)
            mock_move.assert_called_once_with("msg_node", self.context)
    
    async def test_process_condition_node_true(self):
        """Тест обработки узла condition (условие истинно)"""
        # Подготовка
        node = create_condition_node("name == 'John'")
        self.context.user_data['answers'] = {'name': 'John'}
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move, \
             patch('telegram_client.handlers.check_condition', return_value=True) as mock_check:
            # Выполнение
            result = await process_condition_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            mock_check.assert_called_once_with({'name': 'John'}, "name == 'John'")
            mock_move.assert_called_once_with("cond_node", self.context, condition_value=True)
    
    async def test_process_condition_node_false(self):
        """Тест обработки узла condition (условие ложно)"""
        # Подготовка
        node = create_condition_node("name == 'John'")
        self.context.user_data['answers'] = {'name': 'Jane'}
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move, \
             patch('telegram_client.handlers.check_condition', return_value=False) as mock_check:
            # Выполнение
            result = await process_condition_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            mock_check.assert_called_once_with({'name': 'Jane'}, "name == 'John'")
            mock_move.assert_called_once_with("cond_node", self.context, condition_value=False)
    
    async def test_process_notification_node(self):
        """Тест обработки узла notification"""
        # Подготовка
        node = create_notification_node("User {name} registered", "telegram", "123456")
        self.context.user_data['answers'] = {'name': 'John'}
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move, \
             patch('telegram_client.handlers.format_str', return_value="User John registered") as mock_format:
            # Выполнение
            result = await process_notification_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            mock_format.assert_called_once_with("User {name} registered", {'name': 'John'})
            self.bot_adapter.send_notification.assert_called_once_with(
                "User John registered", "telegram", "123456"
            )
            self.bot_adapter.save_message.assert_called_once_with(
                789, "[Уведомление] User John registered", is_user=False
            )
            mock_move.assert_called_once_with("notif_node", self.context)
    
    async def test_process_datawrite_node(self):
        """Тест обработки узла datawrite"""
        # Подготовка
        pairs = [
            {"variable": "user_type", "value": "premium"},
            {"variable": "status", "value": "active"}
        ]
        node = create_datawrite_node(pairs)
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move, \
             patch('telegram_client.handlers.save_answers_to_form_fields', new_callable=AsyncMock) as mock_save:
            
            # Выполнение
            result = await process_datawrite_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            self.assertEqual(self.context.user_data['answers']['user_type'], 'premium')
            self.assertEqual(self.context.user_data['answers']['status'], 'active')
            mock_save.assert_called_once_with(789, self.context.user_data['answers'])
            mock_move.assert_called_once_with("data_node", self.context)
    
    async def test_process_form_node_no_fields(self):
        """Тест обработки узла form без полей"""
        # Подготовка
        node = create_form_node([])  # Пустой список полей
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move:
            # Выполнение
            result = await process_form_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            self.bot_adapter.send_message.assert_called_once_with(self.update, 'В форме нет полей.')
            self.bot_adapter.save_message.assert_called_once_with(789, 'В форме нет полей.', is_user=False)
            mock_move.assert_called_once_with("form_node", self.context)
    
    async def test_process_form_node_finished(self):
        """Тест обработки узла form (форма завершена)"""
        # Подготовка
        node = create_form_node([{"name": "email", "type": "text"}])
        
        with patch('telegram_client.handlers.ask_form_field', new_callable=AsyncMock) as mock_ask_form_field, \
             patch('telegram_client.handlers.save_answers_to_form_fields', new_callable=AsyncMock) as mock_save:
            
            # Настраиваем мок для возврата FINISHED из form.py (это число 1)
            from telegram_client.logic.form import FINISHED as FORM_FINISHED
            mock_ask_form_field.return_value = FORM_FINISHED
            
            # Выполнение
            result = await process_form_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            self.assertNotIn('fields', self.context.user_data)  # Поля должны быть удалены
            mock_save.assert_called_once_with(789, self.context.user_data['answers'])
    
    async def test_process_form_node_asking(self):
        """Тест обработки узла form (ожидание ввода)"""
        # Подготовка
        node = create_form_node([{"name": "email", "type": "text"}])
        
        with patch('telegram_client.handlers.ask_form_field', new_callable=AsyncMock) as mock_ask_form_field:
            # Настраиваем мок для возврата ASKING (это число 0)
            mock_ask_form_field.return_value = 0  # ASKING = 0
            
            # Выполнение
            result = await process_form_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, WAIT_USER_INPUT)
            self.assertEqual(self.context.user_data['fields'], [{"name": "email", "type": "text"}])
            self.assertEqual(self.context.user_data['field_idx'], 0)
    
    async def test_process_menu_node_first_time(self):
        """Тест обработки узла menu (первый раз)"""
        # Подготовка
        buttons = [
            {"label": "Option 1", "id": "opt1"},
            {"label": "Option 2", "id": "opt2"}
        ]
        node = create_menu_node(buttons, "Choose option:")
        
        # Выполнение
        result = await process_menu_node(self.update, self.context, node, self.bot_adapter)
        
        # Проверки
        self.assertEqual(result, WAIT_USER_INPUT)
        self.bot_adapter.send_menu.assert_called_once_with(self.update, "Choose option:", buttons)
        self.bot_adapter.save_message.assert_called_once_with(789, "Choose option:", is_user=False)
        self.assertTrue(self.context.user_data['asked'])
    
    async def test_process_menu_node_user_choice(self):
        """Тест обработки узла menu (пользователь сделал выбор)"""
        # Подготовка
        buttons = [
            {"label": "Option 1", "id": "opt1"},
            {"label": "Option 2", "id": "opt2"}
        ]
        node = create_menu_node(buttons, "Choose option:")
        self.context.user_data['asked'] = True
        self.update.message.text = "Option 1"
        
        with patch('telegram_client.handlers.move_to_next_node', new_callable=AsyncMock) as mock_move:
            # Выполнение
            result = await process_menu_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, CONTINUE_SCENARIO)
            self.assertNotIn('asked', self.context.user_data)
            mock_move.assert_called_once_with("opt1", self.context, for_btn=True)
    
    async def test_process_break_node(self):
        """Тест обработки узла break"""
        # Подготовка
        node = create_break_node()
        mock_graph = {'start_node': 'start'}
        self.context.user_data['graph'] = mock_graph
        
        with patch('telegram_client.handlers.get_start', return_value={'id': 'start'}) as mock_get_start:
            # Выполнение
            result = await process_break_node(self.update, self.context, node, self.bot_adapter)
            
            # Проверки
            self.assertEqual(result, END_CONVERSATION)
            mock_get_start.assert_called_once_with(mock_graph)
            self.assertEqual(self.context.user_data['node'], 'start')


class TestMoveToNextNode(unittest.TestCase):
    """Тесты для функции move_to_next_node"""
    
    def setUp(self):
        """Настройка тестов"""
        self.context = create_mock_context_with_scenario()
    
    async def test_move_to_next_node_simple(self):
        """Тест простого перехода к следующему узлу"""
        with patch('telegram_client.handlers.get_next_node_id_by_source_id', return_value='next_node') as mock_get_next:
            # Выполнение
            await move_to_next_node('current_node', self.context)
            
            # Проверки
            mock_get_next.assert_called_once_with(
                'current_node', 
                self.context.user_data['graph'], 
                condition_value=None,
                for_btn=False
            )
            self.assertEqual(self.context.user_data['node'], 'next_node')
    
    async def test_move_to_next_node_with_condition(self):
        """Тест перехода к следующему узлу с условием"""
        with patch('telegram_client.handlers.get_next_node_id_by_source_id', return_value='true_branch') as mock_get_next:
            # Выполнение
            await move_to_next_node('condition_node', self.context, condition_value=True)
            
            # Проверки
            mock_get_next.assert_called_once_with(
                'condition_node', 
                self.context.user_data['graph'], 
                condition_value=True,
                for_btn=False
            )
            self.assertEqual(self.context.user_data['node'], 'true_branch')


def run_async_test(coro):
    """Хелпер для запуска асинхронных тестов"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Преобразуем асинхронные тесты в синхронные
for name in dir(TestHandlers):
    if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestHandlers, name)):
        test_method = getattr(TestHandlers, name)
        setattr(TestHandlers, name, lambda self, method=test_method: run_async_test(method(self)))

for name in dir(TestMoveToNextNode):
    if name.startswith('test_') and asyncio.iscoroutinefunction(getattr(TestMoveToNextNode, name)):
        test_method = getattr(TestMoveToNextNode, name)
        setattr(TestMoveToNextNode, name, lambda self, method=test_method: run_async_test(method(self)))


if __name__ == '__main__':
    unittest.main()
