"""
Функции для работы с контекстом чата и пользователя.
"""
import json
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes

from telegram_client import django_client
from telegram_client.utils import get_node_by_id

logger = logging.getLogger(__name__)


def get_current_node(context: ContextTypes.DEFAULT_TYPE):
    """Получить текущий узел из контекста"""
    node_id = context.user_data.get('node', None)
    if node_id is None:
        return None
    return get_node_by_id(node_id, context.user_data['graph'])


async def update_chat_context(chat_id, context_data):
    """Обновить контекст чата в базе данных"""
    if chat_id and context_data:
        await django_client.update_chat_context(chat_id, context_data)


async def save_bot_message(chat_id, text):
    """Сохранить сообщение бота в базу данных"""
    if chat_id and text:
        await django_client.create_message(
            chat_id=chat_id,
            text=text,
            is_user_message=False
        )


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
    # Если chat_id уже есть, проверяем, что чат действительно существует
    if context.user_data.get('chat_id'):
        try:
            # Проверяем существование чата через Django ORM
            from asgiref.sync import sync_to_async
            from apps.chats.models import Chat
            
            @sync_to_async
            def check_chat_exists(chat_id):
                return Chat.objects.filter(id=chat_id).exists()
            
            chat_exists = await check_chat_exists(context.user_data['chat_id'])
            if chat_exists:
                return  # Чат существует, всё в порядке
            else:
                # Чат не существует, нужно создать новый
                logger.warning(f"Чат с id {context.user_data['chat_id']} не существует, создаем новый")
                context.user_data.pop('chat_id', None)  # Удаляем неправильный chat_id
        except Exception as e:
            logger.error(f"Ошибка проверки существования чата: {e}")
            context.user_data.pop('chat_id', None)  # Удаляем chat_id при ошибке
    
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


async def ensure_scenario_initialized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обеспечить инициализацию сценария"""
    if not context.user_data.get('scenario_id'):
        import os
        bot_id = os.environ.get("BOT_ID")
        scenario = await django_client.get_scenario_by_bot(bot_id)
        if not scenario:
            error_message = 'Нет доступных сценариев.'
            await update.message.reply_text(error_message)
            # Сохраняем сообщение бота
            await save_bot_message(context.user_data.get('chat_id'), error_message)
            from telegram.ext import ConversationHandler
            return ConversationHandler.END
        
        import json
        context.user_data['scenario_id'] = scenario.id
        context.user_data['graph'] = json.loads(scenario.graph)
        context.user_data['answers'] = {}
    
    return None  # Успешная инициализация


async def ensure_node_initialized(context: ContextTypes.DEFAULT_TYPE):
    """Обеспечить инициализацию текущего узла"""
    node_id = context.user_data.get('node', None)
    if node_id is None:
        from telegram_client.utils import get_start
        context.user_data["node"] = get_start(context.user_data['graph'])["id"]


async def save_context_to_database(context: ContextTypes.DEFAULT_TYPE):
    """Сохранить контекст пользователя в базу данных"""
    if not context.user_data.get('chat_id'):
        return
    
    # Обновляем контекст чата с текущими данными пользователя
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


async def save_bot_message(chat_id, text):
    """Сохранить сообщение бота в базу данных"""
    if chat_id and text:
        await django_client.create_message(
            chat_id=chat_id,
            text=text,
            is_user_message=False
        )
