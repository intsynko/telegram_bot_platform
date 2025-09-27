"""
Моки и фикстуры для тестирования telegram_client
"""
from unittest.mock import Mock, AsyncMock


class MockTelegramUser:
    """Мок для telegram.User"""
    def __init__(self, user_id=123456789, username='testuser', first_name='Test', last_name='User'):
        self.id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.is_bot = False


class MockTelegramChat:
    """Мок для telegram.Chat"""
    def __init__(self, chat_id=987654321, chat_type='private'):
        self.id = chat_id
        self.type = chat_type


class MockTelegramMessage:
    """Мок для telegram.Message"""
    def __init__(self, message_id=1, text='/start', user=None, chat=None):
        self.message_id = message_id
        self.text = text
        self.from_user = user or MockTelegramUser()
        self.chat = chat or MockTelegramChat()
        self.reply_text = AsyncMock()


class MockTelegramUpdate:
    """Мок для telegram.Update"""
    def __init__(self, update_id=1, message=None, user=None, chat=None):
        self.update_id = update_id
        self.message = message or MockTelegramMessage(
            text='/start',
            user=user or MockTelegramUser(),
            chat=chat or MockTelegramChat()
        )
        self.effective_user = self.message.from_user
        self.effective_chat = self.message.chat


class MockTelegramContext:
    """Мок для telegram.ext.ContextTypes.DEFAULT_TYPE"""
    def __init__(self, user_data=None, bot_data=None, chat_data=None):
        self.user_data = user_data or {}
        self.bot_data = bot_data or {}
        self.chat_data = chat_data or {}
        self.bot = Mock()
        self.job_queue = Mock()


class MockTelegramApplication:
    """Мок для telegram.ext.Application"""
    def __init__(self, token='fake_token'):
        self.token = token
        self.bot = Mock()
        self.handlers = []
        
    def add_handler(self, handler):
        """Добавить handler"""
        self.handlers.append(handler)
        
    def run_polling(self):
        """Мок запуска polling"""
        pass


def create_test_scenario_graph():
    """Создает тестовый граф сценария"""
    return {
        "nodes": [
            {
                "id": "start",
                "type": "message",
                "data": {"text": "Добро пожаловать! Как вас зовут?"}
            },
            {
                "id": "name_form",
                "type": "form",
                "data": {
                    "question": "Введите ваше имя:",
                    "field": "name"
                }
            },
            {
                "id": "age_form", 
                "type": "form",
                "data": {
                    "question": "Сколько вам лет?",
                    "field": "age"
                }
            },
            {
                "id": "condition_adult",
                "type": "condition",
                "data": {
                    "expression": "age >= 18"
                }
            },
            {
                "id": "adult_message",
                "type": "message",
                "data": {"text": "Отлично, {name}! Вы совершеннолетний."}
            },
            {
                "id": "minor_message",
                "type": "message", 
                "data": {"text": "Привет, {name}! Вы еще несовершеннолетний."}
            },
            {
                "id": "notification",
                "type": "notification",
                "data": {
                    "type": "telegram",
                    "chat_id": "123456789",
                    "message": "Новый пользователь: {name}, возраст: {age}"
                }
            },
            {
                "id": "datawrite",
                "type": "datawrite",
                "data": {
                    "pairs": [
                        {"field": "full_name", "value": "{name}"},
                        {"field": "user_age", "value": "{age}"}
                    ]
                }
            },
            {
                "id": "end",
                "type": "message",
                "data": {"text": "Спасибо за регистрацию!"}
            }
        ],
        "edges": [
            {"source": "start", "target": "name_form"},
            {"source": "name_form", "target": "age_form"},
            {"source": "age_form", "target": "condition_adult"},
            {"source": "condition_adult", "target": "adult_message", "condition": True},
            {"source": "condition_adult", "target": "minor_message", "condition": False},
            {"source": "adult_message", "target": "notification"},
            {"source": "minor_message", "target": "notification"},
            {"source": "notification", "target": "datawrite"},
            {"source": "datawrite", "target": "end"}
        ]
    }


def create_simple_scenario_graph():
    """Создает простой тестовый граф сценария"""
    return {
        "nodes": [
            {
                "id": "start",
                "type": "message",
                "data": {"text": "Привет! Как дела?"}
            },
            {
                "id": "name_form",
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
            {"source": "start", "target": "name_form"},
            {"source": "name_form", "target": "end"}
        ]
    }


class TelegramTestFixtures:
    """Фикстуры для тестирования telegram_client"""
    
    @staticmethod
    def create_update_with_start_command():
        """Создает Update с командой /start"""
        return MockTelegramUpdate(
            message=MockTelegramMessage(text='/start')
        )
    
    @staticmethod
    def create_update_with_text(text='Hello'):
        """Создает Update с текстовым сообщением"""
        return MockTelegramUpdate(
            message=MockTelegramMessage(text=text)
        )
    
    @staticmethod
    def create_context_with_data(user_data=None):
        """Создает Context с пользовательскими данными"""
        return MockTelegramContext(user_data=user_data or {})
    
    @staticmethod
    def create_context_with_chat_and_scenario(chat_id, scenario_id, graph=None):
        """Создает Context с данными чата и сценария"""
        return MockTelegramContext(user_data={
            'chat_id': chat_id,
            'scenario_id': scenario_id,
            'graph': graph or create_simple_scenario_graph(),
            'node': 'start',
            'answers': {}
        })


# Константы для тестов
TEST_USER_ID = 123456789
TEST_USERNAME = 'testuser'
TEST_CHAT_ID = 987654321
TEST_BOT_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
TEST_SYSTEM_BOT_TOKEN = '654321:XYZ-ABC9876fedcba-123'


def patch_telegram_imports():
    """
    Возвращает словарь для патчинга импортов telegram
    Использовать с @patch.dict('sys.modules', patch_telegram_imports())
    """
    telegram_mock = Mock()
    telegram_mock.Update = MockTelegramUpdate
    telegram_mock.ReplyKeyboardMarkup = Mock()
    telegram_mock.KeyboardButton = Mock()
    
    telegram_ext_mock = Mock()
    telegram_ext_mock.Application = MockTelegramApplication
    telegram_ext_mock.CommandHandler = Mock()
    telegram_ext_mock.MessageHandler = Mock()
    telegram_ext_mock.filters = Mock()
    telegram_ext_mock.ContextTypes = Mock()
    telegram_ext_mock.ContextTypes.DEFAULT_TYPE = MockTelegramContext
    telegram_ext_mock.ConversationHandler = Mock()
    
    return {
        'telegram': telegram_mock,
        'telegram.ext': telegram_ext_mock
    }
