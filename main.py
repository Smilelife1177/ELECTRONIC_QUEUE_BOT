import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from brain import QueueManager

# Завантаження змінних із .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Конфіг підключення до MySQL
db_config = {
    'user': 'bot_user',
    'password': os.getenv('MYSQL_PASSWORD', '7730130'),
    'host': 'localhost',
    'database': 'telegram_queue'
}

# Логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()
queue_manager = QueueManager(db_config)

# Кнопка для надсилання номера
def get_contact_keyboard() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Поділитися номером телефону", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

# Основне меню
def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Записатися в чергу", callback_data='join')],
        [InlineKeyboardButton(text="Покинути чергу", callback_data='leave')],
        [InlineKeyboardButton(text="Переглянути чергу", callback_data='view')],
        [InlineKeyboardButton(text="Наступний!", callback_data='next')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Анонім"
    logger.info(f"/start від {user_id} ({user_name})")

    phone_number = await queue_manager.phone_exists(user_id)
    if phone_number:
        await message.answer("Вітаю знову! Оберіть дію:", reply_markup=get_main_keyboard())
    else:
        await message.answer("Вітаю! Щоб продовжити, поділіться своїм номером телефону:", reply_markup=get_contact_keyboard())

# Обробка контакту
@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: types.Message):
    contact = message.contact
    user_id = contact.user_id
    phone_number = contact.phone_number
    user_name = message.from_user.first_name or "Анонім"

    logger.info(f"📞 Отримано номер: {phone_number} від {user_name} (ID: {user_id})")
    await queue_manager.save_user_phone(user_id, user_name, phone_number)

    await message.answer(
        "✅ Дякую! Ваш номер збережено.\nОберіть дію нижче:",
        reply_markup=get_main_keyboard()
    )

# /stats
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    stats = queue_manager.get_stats()
    await message.answer(stats, reply_markup=get_main_keyboard())

# Обробка кнопок
@dp.callback_query()
async def button_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Анонім"
    chat_id = callback.message.chat.id

    logger.info(f"🔘 callback {callback.data} від {user_id} ({user_name})")

    try:
        if callback.data == 'join':
            phone_number = await queue_manager.phone_exists(user_id)
            if not phone_number:
                await callback.message.edit_text(
                    "Будь ласка, спочатку поділіться номером телефону за допомогою /start.",
                    reply_markup=get_main_keyboard()
                )
                await callback.answer()
                return
            response = queue_manager.join_queue(user_id, user_name)
            await queue_manager.save_queue()

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
        logger.error(f"❌ callback {callback.data}: {e}")
        await callback.message.edit_text("Сталася помилка. Спробуйте ще раз.")
        await callback.answer()

# Перевірка токену
async def check_token():
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Токен коректний: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Токен не працює: {e}")
        return False

# Вимкнути вебхуки
async def disable_webhook():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🌐 Вебхуки вимкнено")
    except Exception as e:
        logger.error(f"Вимкнення вебхуків: {e}")

# Обробка завершення
async def shutdown():
    logger.info("Завершення роботи бота...")
    await queue_manager.clear_queue()
    await bot.session.close()
    logger.info("Бот зупинений")

# Основна функція
async def main():
    try:
        logger.info("🔄 Запуск бота...")
        if not await check_token():
            raise ValueError("❌ Невірний TELEGRAM_TOKEN у .env")
        await disable_webhook()
        await queue_manager.startup()
        logger.info("✅ Бот працює!")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.critical(f"❌ Критична помилка: {e}")
        raise
    finally:
        await shutdown()

if __name__ == '__main__':
    asyncio.run(main())