import logging
import os
import re
from datetime import datetime

logging.basicConfig(
    level=logging.INFO
)

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram_client import django_client
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

ASKING, = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):


    return await run_scenario(update, context)


async def run_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('greeted'):
        await update.message.reply_text('Привет! Я бот для прохождения сценариев.', reply_markup=ReplyKeyboardMarkup([]))
        context.user_data['greeted'] = True
    if not context.user_data.get('scenario_id'):
        scenario = await django_client.get_first_scenario()
        if not scenario:
            await update.message.reply_text('Нет доступных сценариев.')
            return ConversationHandler.END
        context.user_data['scenario_id'] = scenario.id
        context.user_data['step'] = 0
        context.user_data['answers'] = {}
    return await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scenario_id = context.user_data.get('scenario_id')
    step = context.user_data.get('step', 0)
    scenario = await django_client.get_scenario_by_id(scenario_id)
    elements = await django_client.get_elements_for_scenario(scenario)
    if step >= len(elements):
        await update.message.reply_text('Сценарий завершён! Спасибо за ответы.')
        return ConversationHandler.END
    element = elements[step]
    if element.action_type == 'form':
        fields = await django_client.get_fields_for_form(element.form_id)
        if not fields:
            await update.message.reply_text('В форме нет полей.')
            context.user_data['step'] += 1
            return await ask_next_question(update, context)
        if not context.user_data.get('fields'):
            context.user_data['fields'] = fields
            context.user_data['field_idx'] = 0
        return await ask_form_field(update, context)
    else:
        await update.message.reply_text('Неизвестный тип действия или не задана форма.')
        context.user_data['step'] += 1
        return await ask_next_question(update, context)


async def ask_form_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    if idx >= len(fields):
        context.user_data['step'] += 1
        return await ask_next_question(update, context)
    if idx >= 0:
        result = await handle_answer(update, context)
        if result == ASKING:
            return ASKING
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
    fields = context.user_data['fields']
    idx = context.user_data['field_idx']
    field = fields[idx - 1]
    value = update.message.text
    # PHONE: получаем номер из контакта
    if field.field_type == 'phone' and update.message.contact:
        value = update.message.contact.phone_number
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
    context.user_data['answers'][field.name] = value
    return True


def run_telegram_bot(token, id):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_scenario))
    # application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    id = os.environ.get("BOT_ID")
    token = os.environ.get("BOT_TOKEN")
    run_telegram_bot(token, id)