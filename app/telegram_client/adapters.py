"""
Адаптеры для внешних сервисов и API.
Обеспечивают абстракцию над внешними зависимостями.
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class TelegramAdapter(ABC):
    """Абстрактный адаптер для работы с Telegram"""
    
    @abstractmethod
    async def send_text_message(self, update: Update, text: str) -> None:
        """Отправить текстовое сообщение"""
        pass
    
    @abstractmethod
    async def send_menu_message(self, update: Update, text: str, buttons: list) -> None:
        """Отправить сообщение с меню"""
        pass
    
    @abstractmethod
    def get_user_id(self, update: Update) -> int:
        """Получить ID пользователя"""
        pass
    
    @abstractmethod
    def get_chat_id(self, update: Update) -> int:
        """Получить ID чата"""
        pass
    
    @abstractmethod
    def get_username(self, update: Update) -> Optional[str]:
        """Получить имя пользователя"""
        pass
    
    @abstractmethod
    def get_message_text(self, update: Update) -> Optional[str]:
        """Получить текст сообщения"""
        pass


class TelegramBotAdapter(TelegramAdapter):
    """Конкретный адаптер для Telegram Bot API"""
    
    async def send_text_message(self, update: Update, text: str) -> None:
        """Отправить текстовое сообщение"""
        try:
            await update.message.reply_text(text)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            raise
    
    async def send_menu_message(self, update: Update, text: str, buttons: list) -> None:
        """Отправить сообщение с меню"""
        try:
            keyboard = ReplyKeyboardMarkup([
                [KeyboardButton(button["label"]) for button in buttons]
            ], one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка отправки меню: {e}")
            raise
    
    def get_user_id(self, update: Update) -> int:
        """Получить ID пользователя"""
        return update.effective_user.id
    
    def get_chat_id(self, update: Update) -> int:
        """Получить ID чата"""
        return update.effective_chat.id
    
    def get_username(self, update: Update) -> Optional[str]:
        """Получить имя пользователя"""
        return update.effective_user.username
    
    def get_message_text(self, update: Update) -> Optional[str]:
        """Получить текст сообщения"""
        if update.message and update.message.text:
            return update.message.text
        return None


class DatabaseAdapter(ABC):
    """Абстрактный адаптер для работы с базой данных"""
    
    @abstractmethod
    async def save_message(self, chat_id: int, text: str, is_user: bool) -> None:
        """Сохранить сообщение в БД"""
        pass
    
    @abstractmethod
    async def get_or_create_chat(self, telegram_user_id: int, telegram_chat_id: int, 
                                bot_id: str, username: str = None, context: dict = None) -> tuple:
        """Получить или создать чат"""
        pass
    
    @abstractmethod
    async def update_chat_context(self, chat_id: int, context: dict) -> None:
        """Обновить контекст чата"""
        pass
    
    @abstractmethod
    async def save_form_field(self, chat_id: int, name: str, value: str) -> None:
        """Сохранить поле формы"""
        pass
    
    @abstractmethod
    async def get_scenario_by_bot(self, bot_id: str) -> Optional[Any]:
        """Получить сценарий по ID бота"""
        pass
    
    @abstractmethod
    async def get_scenario_by_id(self, scenario_id: int) -> Optional[Any]:
        """Получить сценарий по ID"""
        pass


class DjangoAdapter(DatabaseAdapter):
    """Конкретный адаптер для Django ORM"""
    
    def __init__(self):
        # Импортируем django_client для делегирования вызовов
        from telegram_client import django_client
        self.django_client = django_client
    
    async def save_message(self, chat_id: int, text: str, is_user: bool) -> None:
        """Сохранить сообщение в БД"""
        await self.django_client.create_message(chat_id, text, is_user)
    
    async def get_or_create_chat(self, telegram_user_id: int, telegram_chat_id: int, 
                                bot_id: str, username: str = None, context: dict = None) -> tuple:
        """Получить или создать чат"""
        return await self.django_client.get_or_create_chat(
            telegram_user_id=telegram_user_id,
            telegram_username=username,
            telegram_chat_id=telegram_chat_id,
            bot_id=bot_id,
            context=context or {}
        )
    
    async def update_chat_context(self, chat_id: int, context: dict) -> None:
        """Обновить контекст чата"""
        await self.django_client.update_chat_context(chat_id, context)
    
    async def save_form_field(self, chat_id: int, name: str, value: str) -> None:
        """Сохранить поле формы"""
        await self.django_client.save_or_update_form_field(chat_id, name, value)
    
    async def get_scenario_by_bot(self, bot_id: str) -> Optional[Any]:
        """Получить сценарий по ID бота"""
        return await self.django_client.get_scenario_by_bot(bot_id)
    
    async def get_scenario_by_id(self, scenario_id: int) -> Optional[Any]:
        """Получить сценарий по ID"""
        return await self.django_client.get_scenario_by_id(scenario_id)


class NotificationAdapter(ABC):
    """Абстрактный адаптер для отправки уведомлений"""
    
    @abstractmethod
    def send_notification(self, message: str, chat_id: str = None) -> None:
        """Отправить уведомление"""
        pass


class TelegramNotificationAdapter(NotificationAdapter):
    """Адаптер для отправки уведомлений через Telegram"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
    
    def send_notification(self, message: str, chat_id: str = None) -> None:
        """Отправить уведомление через Telegram"""
        if not self.bot_token:
            logger.info(f"Уведомление (не отправлено, нет токена): {message}")
            return
        
        try:
            from telegram_client.utils import TelegramConnector
            connector = TelegramConnector(self.bot_token, chat_id)
            connector.send_message(message)
            logger.info(f"Уведомление отправлено: {message}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")


class EmailNotificationAdapter(NotificationAdapter):
    """Адаптер для отправки уведомлений по email"""
    
    def send_notification(self, message: str, chat_id: str = None) -> None:
        """Отправить уведомление по email"""
        # Заглушка для email уведомлений
        logger.info(f"Email уведомление: {message}")


class BotAdapter:
    """Главный адаптер бота, объединяющий все внешние зависимости"""
    
    def __init__(self, telegram_adapter: TelegramAdapter, 
                 database_adapter: DatabaseAdapter,
                 notification_adapters: Dict[str, NotificationAdapter] = None):
        self.telegram = telegram_adapter
        self.database = database_adapter
        self.notifications = notification_adapters or {}
    
    async def send_message(self, update: Update, text: str) -> None:
        """Отправить сообщение пользователю"""
        await self.telegram.send_text_message(update, text)
    
    async def send_menu(self, update: Update, text: str, buttons: list) -> None:
        """Отправить меню пользователю"""
        await self.telegram.send_menu_message(update, text, buttons)
    
    async def save_message(self, chat_id: int, text: str, is_user: bool = False) -> None:
        """Сохранить сообщение в БД"""
        await self.database.save_message(chat_id, text, is_user)
    
    async def save_form_field(self, chat_id: int, name: str, value: str) -> None:
        """Сохранить поле формы"""
        await self.database.save_form_field(chat_id, name, value)
    
    def send_notification(self, message: str, notification_type: str = 'telegram', chat_id: str = None) -> None:
        """Отправить уведомление"""
        if notification_type in self.notifications:
            self.notifications[notification_type].send_notification(message, chat_id)
        else:
            logger.warning(f"Неизвестный тип уведомления: {notification_type}")
    
    def get_user_data(self, update: Update) -> Dict[str, Any]:
        """Получить данные пользователя из update"""
        return {
            'user_id': self.telegram.get_user_id(update),
            'chat_id': self.telegram.get_chat_id(update),
            'username': self.telegram.get_username(update),
            'message_text': self.telegram.get_message_text(update)
        }


def create_bot_adapter(system_bot_token: str = None) -> BotAdapter:
    """Фабрика для создания главного адаптера бота"""
    # Создаем адаптеры
    telegram_adapter = TelegramBotAdapter()
    database_adapter = DjangoAdapter()
    
    # Создаем адаптеры уведомлений
    notification_adapters = {}
    if system_bot_token:
        notification_adapters['telegram'] = TelegramNotificationAdapter(system_bot_token)
    notification_adapters['email'] = EmailNotificationAdapter()
    
    # Создаем главный адаптер
    return BotAdapter(
        telegram_adapter=telegram_adapter,
        database_adapter=database_adapter,
        notification_adapters=notification_adapters
    )
