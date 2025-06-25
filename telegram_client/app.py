import logging
import os
import re
from datetime import datetime

from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from telegram_client import django_client

from apps.menu.models import MenuField
from telegram_client.logic.conditions import check_condition
from telegram_client.logic.form import ask_form_field

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING, FINISHED = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await run_scenario(update, context)


async def run_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        step = 0
    element = elements[step]
    if element.action_type == 'form':
        fields = await django_client.get_fields_for_form(element.form_id)
        form = await django_client.get_form(form_id=element.form_id)
        context.user_data['form_id'] = element.form_id
        context.user_data['form'] = form
        if not fields:
            await update.message.reply_text('В форме нет полей.')
            context.user_data['step'] += 1
            return await ask_next_question(update, context)
        if not context.user_data.get('fields'):
            context.user_data['fields'] = fields
            context.user_data['field_idx'] = 0
        result = await ask_form_field(update, context)
        if result == FINISHED:
            return await ask_next_question(update, context)
        return result
    elif element.action_type == 'menu':
        fields = await django_client.get_fields_for_menu(element.menu_id)
        menu = await django_client.get_menu(element.menu_id)
        if context.user_data.get('asked'):
            del context.user_data['asked']
            value = update.message.text
            for field in fields:
                if value == field.name:
                    if field.field_type == MenuField.SCENARIO_ELEMENT_LINK:
                        next_step = next(
                            (
                                index
                                for index, element in enumerate(elements)
                                if element.id == field.linked_element_id
                            ),
                            None
                        )
                        context.user_data['step'] = next_step
                        return await ask_next_question(update, context)
        keyboard = ReplyKeyboardMarkup([
            [
                KeyboardButton(field.name)
                for field in fields
                if (
                    field.show_condition
                    and check_condition(context.user_data['answers'], field.show_condition)
                )
            ]
        ], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(menu.name, reply_markup=keyboard)
        context.user_data['asked'] = True
    elif element.action_type == 'break':
        context.user_data['step'] += 1
        return ConversationHandler.END
    else:
        await update.message.reply_text('Неизвестный тип действия или не задана форма.')
        context.user_data['step'] += 1
        return await run_scenario(update, context)





def run_telegram_bot(token, id):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.CONTACT, run_scenario))
    application.run_polling()


if __name__ == '__main__':
    id = os.environ.get("BOT_ID")
    token = os.environ.get("BOT_TOKEN")
    run_telegram_bot(token, id)