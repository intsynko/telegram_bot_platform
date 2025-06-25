import logging
import os
import re
from datetime import datetime

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from telegram_client import django_client

from apps.menu.models import MenuField
from telegram_client.logic.conditions import check_condition

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING, FINISHED = range(2)


async def ask_form_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    form = context.user_data['form']
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    if idx > 0 and idx <= len(fields):
        result = await handle_answer(update, context)
        if result == ASKING:
            return ASKING
    if idx >= len(fields):
        context.user_data['step'] += 1
        if form.final_message:
            await update.message.reply_text(form.final_message,reply_markup=ReplyKeyboardMarkup([]))
        return FINISHED
        # return await ask_next_question(update, context)
    field = fields[idx]
    context.user_data['field_idx'] += 1

    # BOOL: кнопки Да/Нет
    if field.field_type == 'bool':
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton('Да'), KeyboardButton('Нет')]
        ], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(f"{field.name} (Да/Нет):", reply_markup=keyboard)
        return ASKING
    # LIST: варианты ответа
    elif field.field_type == 'list':
        # Предполагаем, что варианты ответа хранятся в field.default_value через запятую
        options = [opt.strip() for opt in (field.default_value or '').split(',') if opt.strip()]
        if not options:
            await update.message.reply_text(f"{field.name} (нет вариантов)")
            context.user_data['field_idx'] += 1
            return await ask_form_field(update, context)
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(opt)] for opt in options],
            one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(f"{field.name} (выберите вариант):", reply_markup=keyboard)
        return ASKING
    # PHONE: кнопка для отправки номера
    elif field.field_type == 'phone':
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton('Отправить номер', request_contact=True)]],
            one_time_keyboard=True, resize_keyboard=True
        )
        await update.message.reply_text(f"{field.name} (отправьте номер):", reply_markup=keyboard)
        return ASKING
    else:
        await update.message.reply_text(f"{field.name} ({field.get_field_type_display()}):", reply_markup=ForceReply())
        return ASKING


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    form = context.user_data['form']
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    field = fields[idx - 1]
    value = update.message.text
    # PHONE: получаем номер из контакта
    if field.field_type == 'phone':
        value = None
        if update.message.contact:
            value = update.message.contact.phone_number

        if not value:
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton('Отправить номер', request_contact=True)]],
                one_time_keyboard=True, resize_keyboard=True
            )
            await update.message.reply_text("Пожалуйста, отправьте номер:", reply_markup=keyboard)
            return ASKING
    # INT: валидация
    if field.field_type == 'int':
        if not value.isdigit():
            await update.message.reply_text('Пожалуйста, введите целое число:')
            return ASKING
    # DATE: валидация (формат YYYY-MM-DD)
    if field.field_type == 'date':
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except Exception:
            await update.message.reply_text('Пожалуйста, введите дату в формате ГГГГ-ММ-ДД:')
            return ASKING
    # TIME: валидация (формат HH:MM)
    if field.field_type == 'time':
        if not re.match(r'^\d{2}:\d{2}$', value):
            await update.message.reply_text('Пожалуйста, введите время в формате ЧЧ:ММ:')
            return ASKING
    if context.user_data['answers'].get(form.name) is None:
        context.user_data['answers'][form.name] = {}
    context.user_data['answers'][form.name][field.name] = value
    return True