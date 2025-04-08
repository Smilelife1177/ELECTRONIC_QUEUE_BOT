import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from collections import deque

# Завантажуємо змінні з .env файлу
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Ініціалізуємо чергу як глобальну змінну
queue = deque()
# Словник для зберігання імен користувачів
user_names = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник команди /start"""
    keyboard = [
        [InlineKeyboardButton("Записатися в чергу", callback_data='join')],
        [InlineKeyboardButton("Покинути чергу", callback_data='leave')],
        [InlineKeyboardButton("Переглянути чергу", callback_data='view')],
        [InlineKeyboardButton("Наступний!", callback_data='next')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        'Вітаю! Це бот електронної черги. Оберіть дію:', 
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник натискань на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_name = query.from_user.first_name or "Анонім"

    if query.data == 'join':
        if user_id not in queue:
            queue.append(user_id)
            user_names[user_id] = user_name
            await query.edit_message_text(
                f'{user_name}, ви додані до черги. Ваш номер: {len(queue)}'
            )
        else:
            await query.edit_message_text('Ви вже в черзі!')

    elif query.data == 'leave':
        if user_id in queue:
            queue.remove(user_id)
            del user_names[user_id]
            await query.edit_message_text('Ви покинули чергу.')
        else:
            await query.edit_message_text('Вас немає в черзі!')

    elif query.data == 'view':
        if not queue:
            await query.edit_message_text('Черга порожня.')
        else:
            queue_list = '\n'.join(f"{i+1}. {user_names[uid]}" for i, uid in enumerate(queue))
            await query.edit_message_text(f'Поточна черга:\n{queue_list}')

    elif query.data == 'next':
        if not queue:
            await query.edit_message_text('Черга порожня.')
        else:
            next_user = queue.popleft()
            next_name = user_names.pop(next_user)
            await query.edit_message_text(f'Наступний: {next_name}')

    # Повертаємо кнопки після кожної дії
    keyboard = [
        [InlineKeyboardButton("Записатися в чергу", callback_data='join')],
        [InlineKeyboardButton("Покинути чергу", callback_data='leave')],
        [InlineKeyboardButton("Переглянути чергу", callback_data='view')],
        [InlineKeyboardButton("Наступний!", callback_data='next')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Оберіть дію:', reply_markup=reply_markup)

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Запускаємо бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()