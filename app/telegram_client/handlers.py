"""
Обработчики различных типов узлов сценария.
"""
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from telegram_client.context import save_answers_to_form_fields, save_bot_message
from telegram_client.utils import format_str, check_condition, get_start, get_next_node_id_by_source_id, TelegramConnector

# Константы
FINISHED = ConversationHandler.END

# Сигналы для управления потоком выполнения
CONTINUE_SCENARIO = "continue_scenario"  # Продолжить выполнение сценария
WAIT_USER_INPUT = "wait_user_input"      # Ожидать ввод пользователя
END_CONVERSATION = "end_conversation"     # Завершить разговор


async def move_to_next_node(node_id: str, context: ContextTypes.DEFAULT_TYPE, condition_value=None, for_btn=False):
    """Переместиться к следующему узлу"""
    next_node_id = get_next_node_id_by_source_id(
        node_id, 
        context.user_data['graph'], 
        condition_value=condition_value,
        for_btn=for_btn
    )
    context.user_data["node"] = next_node_id


async def process_message_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа message"""
    message_text = format_str(node["data"]["text"], context.user_data['answers'])
    await update.message.reply_text(message_text)
    # Сохраняем сообщение бота
    await save_bot_message(context.user_data.get('chat_id'), message_text)
    await move_to_next_node(node["id"], context)
    
    # Возвращаем сигнал для продолжения сценария
    return CONTINUE_SCENARIO


async def process_condition_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа condition"""
    condition_result = check_condition(context.user_data['answers'], node["data"]["expression"])
    await move_to_next_node(node["id"], context, condition_value=condition_result)
    
    # Возвращаем сигнал для продолжения сценария
    return CONTINUE_SCENARIO


async def process_notification_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа notification"""
    text = format_str(node["data"]["message"], context.user_data['answers'])
    if node["data"]["type"] == 'telegram':
        tg_connector = TelegramConnector(os.environ.get("SYSTEM_BOT_TOKEN"), node["data"]["chat_id"])
        tg_connector.send_message(text)
    elif node["data"]["type"] == 'email':
        pass
    # Сохраняем сообщение бота (уведомление)
    await save_bot_message(context.user_data.get('chat_id'), f"[Уведомление] {text}")
    await move_to_next_node(node["id"], context)
    
    # Возвращаем сигнал для продолжения сценария
    return CONTINUE_SCENARIO


async def process_datawrite_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа datawrite"""
    for pair in node["data"]["pairs"]:
        variable, value = pair["variable"], pair["value"]
        context.user_data['answers'][variable] = value
    
    # Сохраняем обновленные answers в FormField
    if context.user_data.get('chat_id'):
        await save_answers_to_form_fields(context.user_data['chat_id'], context.user_data['answers'])
    
    await move_to_next_node(node["id"], context)
    
    # Возвращаем сигнал для продолжения сценария
    return CONTINUE_SCENARIO


async def process_break_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа break"""
    context.user_data['node'] = get_start(context.user_data['graph'])["id"]
    return END_CONVERSATION


async def process_form_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа form"""
    context.user_data['form'] = node
    if not node["data"]["fields"]:
        error_message = 'В форме нет полей.'
        await update.message.reply_text(error_message)
        # Сохраняем сообщение бота

        await save_bot_message(context.user_data.get('chat_id'), error_message)
        await move_to_next_node(node["id"], context)
        
        # Возвращаем сигнал для продолжения сценария
        return CONTINUE_SCENARIO
    
    if not context.user_data.get('fields'):
        context.user_data['fields'] = node["data"]['fields']
        context.user_data['field_idx'] = 0
    
    # Обрабатываем форму
    from telegram_client.utils import ask_form_field
    result = await ask_form_field(update, context)
    if result == FINISHED:
        del context.user_data['fields']
        # Сохраняем answers после завершения формы
        if context.user_data.get('chat_id'):
            await save_answers_to_form_fields(context.user_data['chat_id'], context.user_data['answers'])
        return CONTINUE_SCENARIO
    
    # Если форма не завершена, ожидаем ввод пользователя
    return WAIT_USER_INPUT


async def process_menu_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа menu"""
    if context.user_data.get('asked'):
        del context.user_data['asked']
        value = update.message.text
        for field in node["data"]["buttons"]:
            if value == field["label"]:
                # Сохраняем выбор пользователя в answers, если нужно
                if 'save_to_answers' in node["data"] and node["data"]["save_to_answers"]:
                    answers_key = node["data"].get("answers_key", "menu_choice")
                    context.user_data['answers'][answers_key] = value
                    # Сохраняем в FormField
                    if context.user_data.get('chat_id'):
                        await save_answers_to_form_fields(context.user_data['chat_id'], context.user_data['answers'])
                
                await move_to_next_node(field["id"], context, for_btn=True)
                
                # Возвращаем сигнал для продолжения сценария
                return CONTINUE_SCENARIO
    
    keyboard = ReplyKeyboardMarkup([
        [
            KeyboardButton(field["label"])
            for field in node["data"]["buttons"]
            # if (
            #     field.show_condition
            #     and check_condition(context.user_data['answers'], field.show_condition)
            # )
        ]
    ], one_time_keyboard=True, resize_keyboard=True)
    text = format_str(node["data"]["label"], context.user_data['answers'])
    await update.message.reply_text(text, reply_markup=keyboard)
    # Сохраняем сообщение бота
    await save_bot_message(context.user_data.get('chat_id'), text)
    context.user_data['asked'] = True
    
    # Ожидаем выбор пользователя
    return WAIT_USER_INPUT
