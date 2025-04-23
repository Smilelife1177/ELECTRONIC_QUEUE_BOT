import os
import asyncio
import logging
import mysql.connector

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from brain import QueueManager

# Завантаження змінних із .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Конфіг підключення до MySQL
db_config = {
    'user': 'bot_user',
    'password': '7730130',  # 🔁 заміни на свій пароль, якщо потрібно
    'host': 'localhost',
    'database': 'telegram_queue'
}

# Налаштування логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ініціалізуємо бота та диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()
queue_manager = QueueManager()

# Додає користувача до таблиці MySQL
def insert_user(user_id, user_name, position):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queue (user_id, user_name, position) VALUES (%s, %s, %s)",
            (user_id, user_name, position)
        )
        conn.commit()
        logger.info(f"✅ Користувач {user_name} (ID: {user_id}) доданий з позицією {position}")
    except mysql.connector.Error as err:
        logger.error(f"❌ Помилка вставки в БД: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Записатися в чергу", callback_data='join')],
        [InlineKeyboardButton(text="Покинути чергу", callback_data='leave')],
        [InlineKeyboardButton(text="Переглянути чергу", callback_data='view')],
        [InlineKeyboardButton(text="Наступний!", callback_data='next')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    logger.info(f"/start від {message.from_user.id} ({message.from_user.username})")
    await message.answer("Вітаю! Це бот електронної черги. Оберіть дію:", reply_markup=get_main_keyboard())

@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    stats = queue_manager.get_stats()
    await message.answer(stats, reply_markup=get_main_keyboard())

@dp.callback_query()
async def button_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Анонім"
    chat_id = callback.message.chat.id
    logger.info(f"callback {callback.data} від {user_id} ({callback.from_user.username})")

    try:
        if callback.data == 'join':
            response = queue_manager.join_queue(user_id, user_name)
            await queue_manager.save_queue()
            insert_user(user_id, user_name, len(queue_manager.queue))

        elif callback.data == 'leave':
            response = queue_manager.leave_queue(user_id)
            await queue_manager.save_queue()

        elif callback.data == 'view':
            response = queue_manager.view_queue()

        elif callback.data == 'next':
            response, updated_users = await queue_manager.next_in_queue()
            await queue_manager.save_queue()
            if queue_manager.queue:
                asyncio.create_task(queue_manager.remind_first(bot, chat_id))
            for uid in updated_users:
                notify_msg = await queue_manager.notify_position(uid)
                await bot.send_message(chat_id=chat_id, text=notify_msg)

        await callback.message.edit_text(response, reply_markup=get_main_keyboard())
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Помилка callback {callback.data}: {e}")
        await callback.message.edit_text("Виникла помилка. Спробуйте ще раз.")
        await callback.answer()

async def check_token():
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Токен коректний: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Токен не працює: {e}")
        return False

async def disable_webhook():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхуки вимкнено")
    except Exception as e:
        logger.error(f"Помилка відключення вебхуків: {e}")

async def main():
    try:
        logger.info("🔄 Запуск бота...")
        if not await check_token():
            raise ValueError("Невірний TELEGRAM_TOKEN у .env")
        await disable_webhook()
        await queue_manager.startup()
        logger.info("✅ Бот запущено. Очікування повідомлень...")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"❌ Критична помилка при запуску: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
