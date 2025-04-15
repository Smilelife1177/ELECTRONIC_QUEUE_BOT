import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from collections import deque
import mysql.connector

# моя гілка O/S
# Завантажуємо змінні з .env файлу
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Налаштування підключення до бази даних
db_config = {
    'user': 'bot_user',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'telegram_queue'
}

# Функція для підключення до бази даних
def get_db_connection():
    return mysql.connector.connect(**db_config)

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

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if query.data == 'join':
            # Перевіряємо, чи користувач уже в черзі
            cursor.execute("SELECT user_id FROM queue WHERE user_id = %s", (user_id,))
            if cursor.fetchone():
                await query.edit_message_text('Ви вже в черзі!')
            else:
                # Отримуємо поточну кількість людей у черзі для визначення позиції
                cursor.execute("SELECT MAX(position) FROM queue")
                max_position = cursor.fetchone()[0]
                new_position = (max_position or 0) + 1

                # Додаємо користувача до черги
                cursor.execute(
                    "INSERT INTO queue (user_id, user_name, position) VALUES (%s, %s, %s)",
                    (user_id, user_name, new_position)
                )
                conn.commit()
                await query.edit_message_text(
                    f'{user_name}, ви додані до черги. Ваш номер: {new_position}'
                )

        elif query.data == 'leave':
            # Перевіряємо, чи користувач у черзі
            cursor.execute("SELECT position FROM queue WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                position = result[0]
                # Видаляємо користувача
                cursor.execute("DELETE FROM queue WHERE user_id = %s", (user_id,))
                # Оновлюємо позиції всіх, хто був після нього
                cursor.execute("UPDATE queue SET position = position - 1 WHERE position > %s", (position,))
                conn.commit()
                await query.edit_message_text('Ви покинули чергу.')
            else:
                await query.edit_message_text('Вас немає в черзі!')

        elif query.data == 'view':
            cursor.execute("SELECT position, user_name FROM queue ORDER BY position")
            queue_list = cursor.fetchall()
            if not queue_list:
                await query.edit_message_text('Черга порожня.')
            else:
                queue_text = '\n'.join(f"{pos}. {name}" for pos, name in queue_list)
                await query.edit_message_text(f'Поточна черга:\n{queue_text}')

        elif query.data == 'next':
            cursor.execute("SELECT user_id, user_name FROM queue WHERE position = 1")
            result = cursor.fetchone()
            if result:
                next_user_id, next_name = result
                # Видаляємо першого користувача
                cursor.execute("DELETE FROM queue WHERE user_id = %s", (next_user_id,))
                # Оновлюємо позиції всіх інших
                cursor.execute("UPDATE queue SET position = position - 1 WHERE position > 1")
                conn.commit()
                await query.edit_message_text(f'Наступний: {next_name}')
            else:
                await query.edit_message_text('Черга порожня.')

        # Повертаємо кнопки після кожної дії
        keyboard = [
            [InlineKeyboardButton("Записатися в чергу", callback_data='join')],
            [InlineKeyboardButton("Покинути чергу", callback_data='leave')],
            [InlineKeyboardButton("Переглянути чергу", callback_data='view')],
            [InlineKeyboardButton("Наступний!", callback_data='next')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Оберіть дію:', reply_markup=reply_markup)

    finally:
        cursor.close()
        conn.close()

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