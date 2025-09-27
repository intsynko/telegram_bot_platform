import json
import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import sys
sys.path.append(os.getcwd())

from telegram_client import django_client
from telegram_client.context import (
    ensure_chat_exists, save_user_message, get_current_node,
    ensure_scenario_initialized, ensure_node_initialized, save_context_to_database,
    save_bot_message
)
from telegram_client.handlers import (
    process_message_node, process_condition_node, process_notification_node,
    process_datawrite_node, process_form_node, process_menu_node, process_break_node,
    CONTINUE_SCENARIO, WAIT_USER_INPUT, END_CONVERSATION
)
from telegram_client.adapters import create_bot_adapter
from telegram_client.utils import get_start

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING, FINISHED = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await run_scenario(update, context)


async def run_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обеспечиваем существование чата и восстанавливаем контекст
    await ensure_chat_exists(update, context)
    
    # Сохраняем сообщение пользователя (исключая команды)
    await save_user_message(update, context, exclude_commands=True)
    
    # Обеспечиваем инициализацию сценария
    result = await ensure_scenario_initialized(update, context)
    if result is not None:  # Если вернулся ConversationHandler.END
        return result
    
    # Обеспечиваем инициализацию текущего узла
    await ensure_node_initialized(context)
    
    # Сохраняем контекст в базу данных
    await save_context_to_database(context)
    
    return await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная функция обработки узлов сценария"""
    # Создаем адаптер бота
    import os
    system_bot_token = os.environ.get("SYSTEM_BOT_TOKEN")
    bot_adapter = create_bot_adapter(system_bot_token)
    
    while True:
        # Получаем текущий узел
        node = get_current_node(context)
        if node is None:
            return FINISHED
        
        # Диспетчер узлов - делегируем обработку специализированным функциям
        node_type = node["type"]
        
        if node_type == 'message':
            signal = await process_message_node(update, context, node, bot_adapter)
        elif node_type == 'condition':
            signal = await process_condition_node(update, context, node, bot_adapter)
        elif node_type == 'notification':
            signal = await process_notification_node(update, context, node, bot_adapter)
        elif node_type == 'datawrite':
            signal = await process_datawrite_node(update, context, node, bot_adapter)
        elif node_type == 'form':
            signal = await process_form_node(update, context, node, bot_adapter)
        elif node_type == 'menu':
            signal = await process_menu_node(update, context, node, bot_adapter)
        elif node_type == 'break':
            signal = await process_break_node(update, context, node, bot_adapter)
        else:
            # Обработка неизвестного типа узла
            error_message = 'Неизвестный тип действия или не задана форма.'
            await bot_adapter.send_message(update, error_message)
            await bot_adapter.save_message(context.user_data.get('chat_id'), error_message, is_user=False)
            context.user_data['node'] = get_start(context.user_data['graph'])["id"]
            return await run_scenario(update, context)
        
        # Обрабатываем сигнал от хендлера
        if signal == CONTINUE_SCENARIO:
            # Продолжаем выполнение сценария (следующая итерация цикла)
            continue
        elif signal == WAIT_USER_INPUT:
            # Ожидаем ввод пользователя - выходим из функции
            return
        elif signal == END_CONVERSATION:
            # Завершаем разговор
            return ConversationHandler.END
        else:
            # Неизвестный сигнал - логируем и завершаем
            logger.warning(f"Неизвестный сигнал от хендлера: {signal}")
            return FINISHED




def run_telegram_bot():
    id = os.environ.get("BOT_ID")
    bot = django_client.get_bot_by_id(id)
    application = Application.builder().token(bot.token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.CONTACT, run_scenario))
    application.run_polling()


if __name__ == '__main__':
    run_telegram_bot()