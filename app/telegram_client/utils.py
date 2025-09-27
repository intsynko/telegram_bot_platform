"""
Вспомогательные функции для telegram_client.
Реэкспорт функций из различных модулей для удобства использования.
"""

# Импорт функций для работы с условиями и форматированием
from .logic.conditions import check_condition, format_str

# Импорт функций для работы с графом сценариев
from .logic.graph import (
    get_start,
    get_node_by_id,
    get_next_node_id_by_source_id
)

# Импорт функций для работы с формами
from .logic.form import ask_form_field

# Импорт коннекторов
from .logic.system_bot import TelegramConnector

# Реэкспорт всех функций для удобства
__all__ = [
    'check_condition',
    'format_str',
    'get_start',
    'get_node_by_id', 
    'get_next_node_id_by_source_id',
    'ask_form_field',
    'TelegramConnector'
]
