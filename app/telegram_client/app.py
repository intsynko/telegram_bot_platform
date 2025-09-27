import json
import logging
import os

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import sys
sys.path.append(os.getcwd())

from telegram_client import django_client

from telegram_client.logic.conditions import check_condition, format_str
from telegram_client.logic.form import ask_form_field
from telegram_client.logic.graph import (
    get_start,
    get_node_by_id,
    get_next_node_id_by_source_id
)
from telegram_client.logic.system_bot import TelegramConnector

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING, FINISHED = range(2)


async def save_bot_message(chat_id, text):
    """Сохранить сообщение бота в базу данных"""
    if chat_id and text:
        await django_client.create_message(
            chat_id=chat_id,
            text=text,
            is_user_message=False
        )


async def update_chat_context(chat_id, context_data):
    """Обновить контекст чата в базе данных"""
    if chat_id and context_data:
        await django_client.update_chat_context(chat_id, context_data)


async def save_answers_to_form_fields(chat_id, answers):
    """Сохранить все answers в FormField"""
    if not chat_id or not answers:
        return
    
    for form_name, form_data in answers.items():
        if isinstance(form_data, dict):
            # Если это словарь (данные формы)
            for field_name, field_value in form_data.items():
                field_name_full = f"{form_name}_{field_name}"
                await django_client.save_or_update_form_field(chat_id, field_name_full, str(field_value))
        else:
            # Если это простое значение
            await django_client.save_or_update_form_field(chat_id, form_name, str(form_data))


async def restore_chat_context(telegram_chat_id, bot_id, context):
    """Восстановить контекст чата из базы данных"""
    try:
        # Получаем контекст чата из базы
        chat_data = await django_client.get_chat_context(telegram_chat_id, bot_id)
        if not chat_data:
            return False
        
        # Восстанавливаем chat_id
        context.user_data['chat_id'] = chat_data['chat_id']
        
        # Восстанавливаем сохраненный контекст
        saved_context = chat_data['context']
        if saved_context:
            # Восстанавливаем основные данные
            if 'scenario_id' in saved_context:
                context.user_data['scenario_id'] = saved_context['scenario_id']
            if 'node' in saved_context:
                context.user_data['node'] = saved_context['node']
            if 'answers' in saved_context:
                context.user_data['answers'] = saved_context['answers']
            if 'form' in saved_context:
                context.user_data['form'] = saved_context['form']
            if 'fields' in saved_context:
                context.user_data['fields'] = saved_context['fields']
            if 'field_idx' in saved_context:
                context.user_data['field_idx'] = saved_context['field_idx']
            if 'asked' in saved_context:
                context.user_data['asked'] = saved_context['asked']
        
        # Восстанавливаем graph если есть scenario_id
        if context.user_data.get('scenario_id'):
            scenario = await django_client.get_scenario_by_id(context.user_data['scenario_id'])
            if scenario:
                context.user_data['graph'] = json.loads(scenario.graph)
        
        # Восстанавливаем answers из FormField
        form_fields = await django_client.get_chat_form_fields(chat_data['chat_id'])
        if form_fields:
            # Группируем поля по формам
            restored_answers = {}
            for field_name, field_value in form_fields.items():
                if '_' in field_name:
                    form_name, field_key = field_name.split('_', 1)
                    if form_name not in restored_answers:
                        restored_answers[form_name] = {}
                    restored_answers[form_name][field_key] = field_value
                else:
                    restored_answers[field_name] = field_value
            
            # Объединяем с существующими answers
            if context.user_data.get('answers'):
                context.user_data['answers'].update(restored_answers)
            else:
                context.user_data['answers'] = restored_answers
        
        logger.info(f"Восстановлен контекст для чата {telegram_chat_id}: {context.user_data}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка восстановления контекста для чата {telegram_chat_id}: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обеспечиваем существование чата и восстанавливаем контекст
    await ensure_chat_exists(update, context)
    
    # Сохраняем сообщение пользователя (включая команды)
    await save_user_message(update, context, exclude_commands=False)
    
    return await run_scenario(update, context)


async def run_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обеспечиваем существование чата и восстанавливаем контекст
    await ensure_chat_exists(update, context)
    
    # Сохраняем сообщение пользователя (исключая команды)
    await save_user_message(update, context, exclude_commands=True)
    
    if not context.user_data.get('scenario_id'):
        id = os.environ.get("BOT_ID")
        scenario = await django_client.get_scenario_by_bot(id)
        if not scenario:
            error_message = 'Нет доступных сценариев.'
            await update.message.reply_text(error_message)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), error_message)
            return ConversationHandler.END
        context.user_data['scenario_id'] = scenario.id
        context.user_data['graph'] = json.loads(scenario.graph)
        context.user_data['answers'] = {}

    node_id = context.user_data.get('node', None)
    if node_id is None:
        context.user_data["node"] = get_start(context.user_data['graph'])["id"]
    
    # Обновляем контекст чата с текущими данными пользователя
    if context.user_data.get('chat_id'):
        chat_context = {
            'scenario_id': context.user_data.get('scenario_id'),
            'node': context.user_data.get('node'),
            'answers': context.user_data.get('answers', {}),
            'form': context.user_data.get('form'),
            'fields': context.user_data.get('fields'),
            'field_idx': context.user_data.get('field_idx'),
            'asked': context.user_data.get('asked')
        }
        await update_chat_context(context.user_data['chat_id'], chat_context)
        
        # Сохраняем все answers в FormField
        answers = context.user_data.get('answers', {})
        if answers:
            await save_answers_to_form_fields(context.user_data['chat_id'], answers)
    
    return await ask_next_question(update, context)


def get_current_node(context: ContextTypes.DEFAULT_TYPE):
    """Получить текущий узел из контекста"""
    node_id = context.user_data.get('node', None)
    if node_id is None:
        return None
    return get_node_by_id(node_id, context.user_data['graph'])


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
    return await ask_next_question(update, context)


async def process_condition_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа condition"""
    condition_result = check_condition(context.user_data['answers'], node["data"]["expression"])
    await move_to_next_node(node["id"], context, condition_value=condition_result)
    return await ask_next_question(update, context)


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
    return await ask_next_question(update, context)


async def process_datawrite_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа datawrite"""
    for pair in node["data"]["pairs"]:
        variable, value = pair["variable"], pair["value"]
        context.user_data['answers'][variable] = value
    
    # Сохраняем обновленные answers в FormField
    if context.user_data.get('chat_id'):
        await save_answers_to_form_fields(context.user_data['chat_id'], context.user_data['answers'])
    
    await move_to_next_node(node["id"], context)
    return await ask_next_question(update, context)


async def process_break_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа break"""
    context.user_data['node'] = get_start(context.user_data['graph'])["id"]
    return ConversationHandler.END


async def process_form_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node: dict):
    """Обработать узел типа form"""
    context.user_data['form'] = node
    if not node["data"]["fields"]:
        error_message = 'В форме нет полей.'
        await update.message.reply_text(error_message)
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), error_message)
        await move_to_next_node(node["id"], context)
        return await ask_next_question(update, context)
    
    if not context.user_data.get('fields'):
        context.user_data['fields'] = node["data"]['fields']
        context.user_data['field_idx'] = 0
    
    result = await ask_form_field(update, context)
    if result == FINISHED:
        del context.user_data['fields']
        # Сохраняем answers после завершения формы
        if context.user_data.get('chat_id'):
            await save_answers_to_form_fields(context.user_data['chat_id'], context.user_data['answers'])
        return await ask_next_question(update, context)
    return result


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
                return await ask_next_question(update, context)
    
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


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная функция обработки узлов сценария"""
    # Получаем текущий узел
    node = get_current_node(context)
    if node is None:
        return FINISHED
    
    # Диспетчер узлов - делегируем обработку специализированным функциям
    node_type = node["type"]
    
    if node_type == 'message':
        return await process_message_node(update, context, node)
    elif node_type == 'condition':
        return await process_condition_node(update, context, node)
    elif node_type == 'notification':
        return await process_notification_node(update, context, node)
    elif node_type == 'datawrite':
        return await process_datawrite_node(update, context, node)
    elif node_type == 'form':
        return await process_form_node(update, context, node)
    elif node_type == 'menu':
        return await process_menu_node(update, context, node)
    elif node_type == 'break':
        return await process_break_node(update, context, node)
    else:
        # Обработка неизвестного типа узла
        error_message = 'Неизвестный тип действия или не задана форма.'
        await update.message.reply_text(error_message)
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), error_message)
        context.user_data['node'] = get_start(context.user_data['graph'])["id"]
        return await run_scenario(update, context)


async def save_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE, exclude_commands: bool = False):
    """Сохранить пользовательское сообщение в БД"""
    if not update.message or not update.message.text:
        return
    
    # Если нужно исключить команды и это команда - не сохраняем
    if exclude_commands and update.message.text.startswith('/'):
        return
    
    await django_client.create_message(
        chat_id=context.user_data['chat_id'],
        text=update.message.text,
        is_user_message=True
    )


async def ensure_chat_exists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обеспечить существование чата и восстановить контекст"""
    # Если chat_id уже есть, ничего не делаем
    if context.user_data.get('chat_id'):
        return
    
    # Получаем данные из update
    bot_id = os.environ.get("BOT_ID")
    telegram_user_id = update.effective_user.id
    telegram_username = update.effective_user.username
    telegram_chat_id = update.effective_chat.id
    
    # Пытаемся восстановить контекст из базы данных
    context_restored = await restore_chat_context(telegram_chat_id, bot_id, context)
    
    if not context_restored:
        # Если контекст не восстановлен, создаем новый чат
        chat, created = await django_client.get_or_create_chat(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            telegram_chat_id=telegram_chat_id,
            bot_id=bot_id,
            context={}
        )
        # Сохраняем chat_id в контексте пользователя
        context.user_data['chat_id'] = chat.id
    else:
        # Контекст восстановлен, обновляем данные пользователя если изменились
        chat, created = await django_client.get_or_create_chat(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            telegram_chat_id=telegram_chat_id,
            bot_id=bot_id,
            context=context.user_data.get('context', {})
        )
        context.user_data['chat_id'] = chat.id


def run_telegram_bot():
    id = os.environ.get("BOT_ID")
    bot = django_client.get_bot_by_id(id)
    application = Application.builder().token(bot.token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.CONTACT, run_scenario))
    application.run_polling()


if __name__ == '__main__':
    run_telegram_bot()