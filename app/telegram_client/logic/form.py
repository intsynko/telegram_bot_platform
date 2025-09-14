import logging
import re
from datetime import datetime

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from telegram_client.logic.graph import get_next_node_id_by_source_id, get_node_by_id
from telegram_client import django_client

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


async def ask_form_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    graph = context.user_data['graph']
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    if idx > 0 and idx <= len(fields):
        result = await handle_answer(update, context)
        if result == ASKING:
            return ASKING
    if idx >= len(fields):
        context.user_data['node'] = get_next_node_id_by_source_id(context.user_data['node'], graph)
        return FINISHED
        # return await ask_next_question(update, context)
    field = fields[idx]
    while field['hidden']:
        idx += 1
        field = fields[idx]
    context.user_data['field_idx'] = idx + 1

    # BOOL: кнопки Да/Нет
    if field["type"] == 'bool':
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton('Да'), KeyboardButton('Нет')]
        ], one_time_keyboard=True, resize_keyboard=True)
        message_text = f"{field['name']} (Да/Нет):"
        await update.message.reply_text(message_text, reply_markup=keyboard)
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), message_text)
        return ASKING
    # LIST: варианты ответа
    elif field["type"] == 'list':
        # Предполагаем, что варианты ответа хранятся в field.default_value через запятую
        options = [opt.strip() for opt in (field.get("default_value") or '').split(',') if opt.strip()]
        if not options:
            message_text = f"{field['name']} (нет вариантов)"
            await update.message.reply_text(message_text)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), message_text)
            context.user_data['field_idx'] += 1
            return await ask_form_field(update, context)
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(opt)] for opt in options],
            one_time_keyboard=True, resize_keyboard=True
        )
        message_text = f"{field['name']} (выберите вариант):"
        await update.message.reply_text(message_text, reply_markup=keyboard)
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), message_text)
        return ASKING
    # PHONE: кнопка для отправки номера
    elif field["type"] == 'phone':
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton('Отправить номер', request_contact=True)]],
            one_time_keyboard=True, resize_keyboard=True
        )
        message_text = f"{field['name']} (отправьте номер):"
        await update.message.reply_text(message_text, reply_markup=keyboard)
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), message_text)
        return ASKING
    else:
        message_text = f"{field['name']}:"
        await update.message.reply_text(message_text, reply_markup=ForceReply())
        # Сохраняем сообщение бота
        await save_bot_message(context.user_data.get('chat_id'), message_text)
        return ASKING


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # form = context.user_data['form']
    node = get_node_by_id(context.user_data['node'], context.user_data['graph'])
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    field = fields[idx - 1]
    value = update.message.text
    # PHONE: получаем номер из контакта
    if field["type"] == 'phone':
        value = None
        if update.message.contact:
            value = update.message.contact.phone_number

        if not value:
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton('Отправить номер', request_contact=True)]],
                one_time_keyboard=True, resize_keyboard=True
            )
            message_text = "Пожалуйста, отправьте номер:"
            await update.message.reply_text(message_text, reply_markup=keyboard)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), message_text)
            return ASKING
    # INT: валидация
    if field["type"] == 'int':
        if not value.isdigit():
            message_text = 'Пожалуйста, введите целое число:'
            await update.message.reply_text(message_text)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), message_text)
            return ASKING
    # DATE: валидация (формат YYYY-MM-DD)
    if field["type"] == 'date':
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except Exception:
            message_text = 'Пожалуйста, введите дату в формате ГГГГ-ММ-ДД:'
            await update.message.reply_text(message_text)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), message_text)
            return ASKING
    # TIME: валидация (формат HH:MM)
    if field["type"] == 'time':
        if not re.match(r'^\d{2}:\d{2}$', value):
            message_text = 'Пожалуйста, введите время в формате ЧЧ:ММ:'
            await update.message.reply_text(message_text)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), message_text)
            return ASKING

    # сохраняем данные опроса
    if context.user_data['answers'].get(node["data"]["label"]) is None:
        context.user_data['answers'][node["data"]["label"]] = {field["name"]: value}
    else:
        context.user_data['answers'][node["data"]["label"]][field["name"]] = value
    
    # Сохраняем значение поля формы в базу данных
    chat_id = context.user_data.get('chat_id')
    if chat_id:
        # Создаем уникальное имя поля: form_label + field_name
        field_name = f"{node['data']['label']}_{field['name']}"
        await django_client.save_or_update_form_field(chat_id, field_name, value)
    
    return True
