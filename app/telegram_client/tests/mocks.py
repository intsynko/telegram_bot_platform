"""
Моки для тестирования telegram_client
"""
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Optional


class MockUpdate:
    """Мок для Telegram Update"""
    
    def __init__(self, message_text: str = "test message", user_id: int = 123, 
                 chat_id: int = 456, username: str = "testuser"):
        self.message = Mock()
        self.message.text = message_text
        self.message.reply_text = AsyncMock()
        
        self.effective_user = Mock()
        self.effective_user.id = user_id
        self.effective_user.username = username
        
        self.effective_chat = Mock()
        self.effective_chat.id = chat_id


class MockContext:
    """Мок для Telegram ContextTypes.DEFAULT_TYPE"""
    
    def __init__(self, user_data: Dict[str, Any] = None):
        self.user_data = user_data or {}


class MockBotAdapter:
    """Мок для BotAdapter"""
    
    def __init__(self):
        self.send_message = AsyncMock()
        self.send_menu = AsyncMock()
        self.save_message = AsyncMock()
        self.save_form_field = AsyncMock()
        self.send_notification = Mock()
        self.get_user_data = Mock()
        
        # Настройка возвращаемых значений
        self.get_user_data.return_value = {
            'user_id': 123,
            'chat_id': 456,
            'username': 'testuser',
            'message_text': 'test message'
        }


class MockTelegramAdapter:
    """Мок для TelegramAdapter"""
    
    def __init__(self):
        self.send_text_message = AsyncMock()
        self.send_menu_message = AsyncMock()
        self.get_user_id = Mock(return_value=123)
        self.get_chat_id = Mock(return_value=456)
        self.get_username = Mock(return_value="testuser")
        self.get_message_text = Mock(return_value="test message")


class MockDatabaseAdapter:
    """Мок для DatabaseAdapter"""
    
    def __init__(self):
        self.save_message = AsyncMock()
        self.get_or_create_chat = AsyncMock()
        self.update_chat_context = AsyncMock()
        self.save_form_field = AsyncMock()
        self.get_scenario_by_bot = AsyncMock()
        self.get_scenario_by_id = AsyncMock()


class MockNotificationAdapter:
    """Мок для NotificationAdapter"""
    
    def __init__(self):
        self.send_notification = Mock()


def create_mock_node(node_type: str, data: Dict[str, Any] = None, node_id: str = "test_node") -> Dict[str, Any]:
    """Создать мок узла сценария"""
    return {
        "id": node_id,
        "type": node_type,
        "data": data or {}
    }


def create_message_node(text: str = "Test message", node_id: str = "msg_node") -> Dict[str, Any]:
    """Создать узел типа message"""
    return create_mock_node("message", {"text": text}, node_id)


def create_condition_node(expression: str = "true", node_id: str = "cond_node") -> Dict[str, Any]:
    """Создать узел типа condition"""
    return create_mock_node("condition", {"expression": expression}, node_id)


def create_notification_node(message: str = "Test notification", 
                           notification_type: str = "telegram",
                           chat_id: str = "123456",
                           node_id: str = "notif_node") -> Dict[str, Any]:
    """Создать узел типа notification"""
    return create_mock_node("notification", {
        "message": message,
        "type": notification_type,
        "chat_id": chat_id
    }, node_id)


def create_datawrite_node(pairs: list = None, node_id: str = "data_node") -> Dict[str, Any]:
    """Создать узел типа datawrite"""
    if pairs is None:
        pairs = [{"variable": "test_var", "value": "test_value"}]
    return create_mock_node("datawrite", {"pairs": pairs}, node_id)


def create_form_node(fields: list = None, node_id: str = "form_node") -> Dict[str, Any]:
    """Создать узел типа form"""
    if fields is None:
        fields = [{"name": "test_field", "type": "text"}]
    return create_mock_node("form", {"fields": fields}, node_id)


def create_menu_node(buttons: list = None, label: str = "Choose option:",
                    node_id: str = "menu_node") -> Dict[str, Any]:
    """Создать узел типа menu"""
    if buttons is None:
        buttons = [
            {"label": "Option 1", "id": "opt1"},
            {"label": "Option 2", "id": "opt2"}
        ]
    return create_mock_node("menu", {
        "buttons": buttons,
        "label": label
    }, node_id)


def create_break_node(node_id: str = "break_node") -> Dict[str, Any]:
    """Создать узел типа break"""
    return create_mock_node("break", {}, node_id)


def create_mock_context_with_scenario(scenario_id: int = 1, 
                                    node_id: str = "current_node",
                                    answers: Dict[str, Any] = None,
                                    chat_id: int = 789) -> MockContext:
    """Создать контекст с инициализированным сценарием"""
    return MockContext({
        'scenario_id': scenario_id,
        'node': node_id,
        'answers': answers or {},
        'chat_id': chat_id,
        'graph': {
            'nodes': [],
            'edges': []
        }
    })


class MockFormField:
    """Мок для ask_form_field"""
    
    def __init__(self, return_value="ASKING"):
        self.return_value = return_value
        self.call_count = 0
        self.call_args = []
    
    async def __call__(self, update, context):
        self.call_count += 1
        self.call_args.append((update, context))
        return self.return_value
