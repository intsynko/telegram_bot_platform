import json
import logging
import os

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from telegram_client import django_client

from telegram_client.logic.conditions import check_condition, format_str
from telegram_client.logic.form import ask_form_field
from telegram_client.logic.graph import (
    get_start,
    get_node_by_id,
    get_next_node_id_by_source_id
)

logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)

ASKING, FINISHED = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await run_scenario(update, context)


async def run_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('scenario_id'):
        id = os.environ.get("BOT_ID")
        scenario = await django_client.get_scenario_by_bot(id)
        if not scenario:
            await update.message.reply_text('Нет доступных сценариев.')
            return ConversationHandler.END
        context.user_data['scenario_id'] = scenario.id
        context.user_data['graph'] = json.loads(scenario.graph)
        context.user_data['answers'] = {}

    node_id = context.user_data.get('node', None)
    if node_id is None:
        context.user_data["node"] = get_start(context.user_data['graph'])["id"]
    return await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scenario_id = context.user_data.get('scenario_id')
    node_id = context.user_data.get('node', None)
    if node_id is None:
        return FINISHED
    else:
        node = get_node_by_id(node_id, context.user_data['graph'])

    if node["type"] == 'message':
        await update.message.reply_text(format_str(node["data"]["text"], context.user_data['answers']))
        context.user_data["node"] = get_next_node_id_by_source_id(node["id"], context.user_data['graph'])
        return await ask_next_question(update, context)
    if node["type"] == 'condition':
        if check_condition(context.user_data['answers'], node["data"]["expression"]):
            context.user_data["node"] = get_next_node_id_by_source_id(node["id"], context.user_data['graph'], condition_value=True)
        else:
            context.user_data["node"] = get_next_node_id_by_source_id(node["id"], context.user_data['graph'], condition_value=False)
        return await ask_next_question(update, context)
    if node["type"] == 'datawrite':
        for pair in node["data"]["pairs"]:
            variable, value = pair["variable"], pair["value"]
            context.user_data['answers'][variable] = value
        context.user_data["node"] = get_next_node_id_by_source_id(node["id"], context.user_data['graph'])
        return await ask_next_question(update, context)
    elif node["type"] == 'form':
        context.user_data['form'] = node
        if not node["data"]["fields"]:
            await update.message.reply_text('В форме нет полей.')
            context.user_data["node"] = get_next_node_id_by_source_id(node["id"], context.user_data['graph'])
            return await ask_next_question(update, context)
        if not context.user_data.get('fields'):
            context.user_data['fields'] = node["data"]['fields']
            context.user_data['field_idx'] = 0
        result = await ask_form_field(update, context)
        if result == FINISHED:
            return await ask_next_question(update, context)
        return result
    elif node["type"] == 'menu':
        if context.user_data.get('asked'):
            del context.user_data['asked']
            value = update.message.text
            for field in node["data"]["buttons"]:
                if value == field["label"]:
                    context.user_data["node"] = get_next_node_id_by_source_id(field["id"], context.user_data['graph'], for_btn=True)
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
        await update.message.reply_text(node["data"]["label"], reply_markup=keyboard)
        context.user_data['asked'] = True
    elif node["type"] == 'break':
        context.user_data['node'] = get_start(context.user_data['graph'])["id"]
        return ConversationHandler.END
    else:
        await update.message.reply_text('Неизвестный тип действия или не задана форма.')
        context.user_data['node'] = get_start(context.user_data['graph'])["id"]
        return await run_scenario(update, context)


def run_telegram_bot():
    id = os.environ.get("BOT_ID")
    bot = django_client.get_bot_by_id(id)
    application = Application.builder().token(bot.token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.CONTACT, run_scenario))
    application.run_polling()


if __name__ == '__main__':
    run_telegram_bot()