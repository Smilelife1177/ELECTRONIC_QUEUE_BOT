import os
import asyncio
import logging
import mysql.connector
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from brain import QueueManager

# Завантаження змінних із .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Конфігурація підключення до MySQL
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
user_context = {}  # {user_id: university_id}

# Визначення станів для введення повідомлення та вибору університету
class BroadcastStates(StatesGroup):
    waiting_for_university = State()
    waiting_for_message = State()

# Словник для зіставлення відображуваних кнопок із діями
BUTTON_MAPPING = {
    "➡️ Почати ⬅️": "Почати",
    "🎓 Вибрати університет 🎓": "Вибрати університет",
    "➕ Записатися в чергу ➕": "Записатися в чергу",
    "➖ Покинути чергу ➖": "Покинути чергу",
    "🔍 Переглянути чергу 🔍": "Переглянути чергу",
    "🪪 Моя позиція 🪪": "Моя позиція",
    "📜 Переглянути історію 📜": "Переглянути історію",
    "⏭️ Видалити першого ⏭️": "Видалити першого",
    "📢 Надіслати оголошення 📢": "Надіслати оголошення"
}

# Функція для очищення тексту від емодзі та пробілів
def clean_button_text(text: str) -> str:
    # Видаляємо емодзі за допомогою regex та зайві пробіли
    text = re.sub(r'[^\w\s]', '', text).strip()
    return text

# Кнопка для надсилання номера
def get_contact_keyboard() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Поділитися номером телефону 📱", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

# Основне меню з кнопками ReplyKeyboardMarkup
async def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    is_admin = await queue_manager.is_admin(user_id)
    keyboard = [
        [KeyboardButton(text="🎓 Вибрати університет 🎓")],
        [KeyboardButton(text="➕ Записатися в чергу ➕")],
        [KeyboardButton(text="➖ Покинути чергу ➖")],
        [KeyboardButton(text="🔍 Переглянути чергу 🔍")],
        [KeyboardButton(text="🪪 Моя позиція 🪪")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="📜 Переглянути історію 📜")])
        keyboard.append([KeyboardButton(text="⏭️ Видалити першого ⏭️")])
        keyboard.append([KeyboardButton(text="📢 Надіслати оголошення 📢")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

# Клавіатура для вибору університету
def get_universities_keyboard(universities) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"uni_{id}")] for id, name in universities]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обробник команди /start"""
    user_id = message.from_user.id
    if user_id in user_context:
        del user_context[user_id]  # Очищаємо контекст для нового акаунта
    logger.info(f"Отримано команду /start від користувача {user_id} ({message.from_user.username})")
    
    start_keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="➡️ Почати ⬅️")
        ]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "Вітаю! Це бот електронної черги. Натисніть 'Почати', щоб обрати дію:",
        reply_markup=start_keyboard
    )

@dp.message(lambda message: message.text == "➡️ Почати ⬅️")
async def handle_start_button(message: types.Message):
    """Обробник натискання кнопки 'Почати'"""
    user_id = message.from_user.id
    logger.info(f"Користувач {user_id} ({message.from_user.username}) натиснув 'Почати' (отриманий текст: '{message.text}')")
    try:
        phone_number = await queue_manager.phone_exists(user_id)
        logger.info(f"Перевірка номера телефону для user_id {user_id}: {'Знайдено: ' + phone_number if phone_number else 'Не знайдено'}")
        if not phone_number:
            await message.answer(
                "Будь ласка, поділіться своїм номером телефону, щоб продовжити:",
                reply_markup=get_contact_keyboard()
            )
        else:
            await message.answer(
                "Оберіть дію:",
                reply_markup=await get_main_keyboard(user_id)
            )
    except Exception as e:
        logger.error(f"Помилка в handle_start_button для user_id {user_id}: {e}")
        await message.answer("Сталася помилка при перевірці номера телефону. Спробуйте ще раз.", reply_markup=get_contact_keyboard())

# Обробка текстових команд від кнопок
@dp.message(lambda message: message.text in BUTTON_MAPPING)
async def button_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Анонім"
    received_text = message.text
    action = BUTTON_MAPPING[received_text]

    logger.info(f"🔘 Кнопка '{received_text}' (дія: {action}) від {user_id} ({user_name})")

    try:
        # Перевірка, чи є користувач адміністратором
        is_admin = await queue_manager.is_admin(user_id)

        if action in ["Переглянути історію", "Видалити першого", "Надіслати оголошення"] and not is_admin:
            await message.answer("Ця дія доступна лише для адміністраторів.", reply_markup=await get_main_keyboard(user_id))
            return

        if action == "Надіслати оголошення":
            universities = await queue_manager.get_universities()
            if not universities:
                await message.answer("Немає доступних університетів.", reply_markup=await get_main_keyboard(user_id))
                return
            await message.answer("Виберіть університет для оголошення:", reply_markup=get_universities_keyboard(universities))
            await state.set_state(BroadcastStates.waiting_for_university)
            return

        if action == "Вибрати університет":
            universities = await queue_manager.get_universities()
            if not universities:
                await message.answer("Немає доступних університетів.")
                return
            await message.answer("Виберіть університет:", reply_markup=get_universities_keyboard(universities))
            return

        # Перевірка, чи вибрано університет (окрім адмінських дій)
        university_id = user_context.get(user_id)
        if not university_id and action not in ["Переглянути історію", "Надіслати оголошення"]:
            await message.answer("Спочатку виберіть університет за допомогою кнопки 'Вибрати університет'.", reply_markup=await get_main_keyboard(user_id))
            return

        if action == "Записатися в чергу":
            phone_number = await queue_manager.phone_exists(user_id)
            if not phone_number:
                await message.answer(
                    "Будь ласка, спочатку поділіться номером телефону за допомогою /start.",
                    reply_markup=get_contact_keyboard()
                )
                return
            response = queue_manager.join_queue(user_id, user_name, university_id)
            await queue_manager.save_queue()

        elif action == "Покинути чергу":
            response = queue_manager.leave_queue(user_id, university_id)
            await queue_manager.save_queue()

        elif action == "Переглянути чергу":
            response = queue_manager.view_queue(university_id)

        elif action == "Моя позиція":
            response = await queue_manager.notify_position(user_id, university_id)

        elif action == "Переглянути історію":
            response = await queue_manager.get_user_history(user_id)

        elif action == "Видалити першого":
            response, updated_users = await queue_manager.next_in_queue(university_id, bot)
            await queue_manager.save_queue()
            if updated_users:
                asyncio.create_task(queue_manager.remind_first(bot, user_id, university_id))

        await message.answer(response, reply_markup=await get_main_keyboard(user_id))

    except Exception as e:
        logger.error(f"❌ Помилка обробки '{action}' (кнопка: {received_text}): {e}")
        await message.answer("Сталася помилка. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))

# Обробка вибору університету для оголошення
@dp.callback_query(StateFilter(BroadcastStates.waiting_for_university), lambda c: c.data.startswith("uni_"))
async def broadcast_university_selection(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Анонім"
    university_id = int(callback.data.split("_")[1])

    logger.info(f"🔘 Вибір університету {university_id} для оголошення від {user_id} ({user_name})")
    
    try:
        await state.update_data(university_id=university_id)
        await callback.message.edit_text("Введіть текст оголошення для користувачів цього університету:")
        await state.set_state(BroadcastStates.waiting_for_message)
        await callback.answer()
    except Exception as e:
        logger.error(f"❌ Помилка вибору університету для оголошення: {e}")
        await callback.message.answer("Сталася помилка. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))
        await state.clear()
        await callback.answer()

# Обробка введення тексту оголошення
@dp.message(StateFilter(BroadcastStates.waiting_for_message))
async def process_broadcast_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Анонім"
    if not await queue_manager.is_admin(user_id):
        await message.answer("Ця дія доступна лише для адміністраторів.", reply_markup=await get_main_keyboard(user_id))
        await state.clear()
        return

    message_text = message.text.strip()
    if not message_text:
        await message.answer("Текст оголошення не може бути порожнім. Спробуйте ще раз.")
        return

    try:
        data = await state.get_data()
        university_id = data.get('university_id')
        if not university_id:
            await message.answer("Не вибрано університет. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))
            await state.clear()
            return

        await queue_manager.broadcast_message(bot, user_id, user_name, message_text, university_id)
        await message.answer("Оголошення успішно надіслано користувачам університету!", reply_markup=await get_main_keyboard(user_id))
        await state.clear()
    except Exception as e:
        logger.error(f"Помилка надсилання оголошення від {user_id}: {e}")
        await message.answer("Сталася помилка при надсиланні оголошення. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))
        await state.clear()

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
        reply_markup=await get_main_keyboard(user_id)
    )

# /stats
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    user_id = message.from_user.id
    university_id = user_context.get(user_id)
    if not university_id:
        await message.answer("Спочатку виберіть університет за допомогою кнопки 'Вибрати університет'.", reply_markup=await get_main_keyboard(user_id))
        return
    stats = queue_manager.get_stats(university_id)
    await message.answer(stats, reply_markup=await get_main_keyboard(user_id))

# /next
@dp.message(Command("next"))
async def next_command(message: types.Message):
    user_id = message.from_user.id
    university_id = user_context.get(user_id)
    if not university_id:
        await message.answer("Спочатку виберіть університет за допомогою кнопки 'Вибрати університет'.", reply_markup=await get_main_keyboard(user_id))
        return
    response, updated_users = await queue_manager.next_in_queue(university_id, bot)
    await queue_manager.save_queue()
    await message.answer(response, reply_markup=await get_main_keyboard(user_id))
    # Нагадування першому в черзі
    if updated_users:
        asyncio.create_task(queue_manager.remind_first(bot, user_id, university_id))

# /remove_first
@dp.message(Command("remove_first"))
async def remove_first_command(message: types.Message):
    user_id = message.from_user.id
    if not await queue_manager.is_admin(user_id):
        await message.answer("Ця команда доступна лише для адміністраторів.", reply_markup=await get_main_keyboard(user_id))
        return
    university_id = user_context.get(user_id)
    if not university_id:
        await message.answer("Спочатку виберіть університет за допомогою кнопки 'Вибрати університет'.", reply_markup=await get_main_keyboard(user_id))
        return
    response, updated_users = await queue_manager.next_in_queue(university_id, bot)
    await queue_manager.save_queue()
    await message.answer(response, reply_markup=await get_main_keyboard(user_id))
    # Нагадування першому в черзі
    if updated_users:
        asyncio.create_task(queue_manager.remind_first(bot, user_id, university_id))

# /admin_history
@dp.message(Command("admin_history"))
async def admin_history_command(message: types.Message):
    user_id = message.from_user.id
    if not await queue_manager.is_admin(user_id):
        await message.answer("Ця команда доступна лише для адміністраторів.", reply_markup=await get_main_keyboard(user_id))
        return
    history = await queue_manager.get_user_history(user_id)
    await message.answer(history, reply_markup=await get_main_keyboard(user_id))

# /broadcast
@dp.message(Command("broadcast"))
async def broadcast_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not await queue_manager.is_admin(user_id):
        await message.answer("Ця команда доступна лише для адміністраторів.", reply_markup=await get_main_keyboard(user_id))
        return
    universities = await queue_manager.get_universities()
    if not universities:
        await message.answer("Немає доступних університетів.", reply_markup=await get_main_keyboard(user_id))
        return
    await message.answer("Виберіть університет для оголошення:", reply_markup=get_universities_keyboard(universities))
    await state.set_state(BroadcastStates.waiting_for_university)

# Обробка вибору університету
@dp.callback_query(lambda c: c.data.startswith("uni_"))
async def university_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Анонім"
    university_id = int(callback.data.split("_")[1])

    logger.info(f"🔘 Вибір університету {university_id} від {user_id} ({user_name})")
    user_context[user_id] = university_id

    try:
        await callback.message.edit_text("Університет вибрано! Оберіть дію:")
        await callback.message.answer("Оберіть дію:", reply_markup=await get_main_keyboard(user_id))
        await callback.answer()
    except Exception as e:
        logger.error(f"❌ Помилка вибору університету: {e}")
        await callback.message.answer("Сталася помилка. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))
        await callback.answer()

# Обробка застарілих кнопок (для сумісності)
@dp.callback_query()
async def button_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "Анонім"
    university_id = user_context.get(user_id)

    logger.info(f"🔘 callback {callback.data} від {user_id} ({user_name})")

    try:
        if not university_id:
            await callback.message.edit_text(
                "Спочатку виберіть університет за допомогою кнопки 'Вибрати університет'.",
                reply_markup=None
            )
            await callback.message.answer("Оберіть дію:", reply_markup=await get_main_keyboard(user_id))
            await callback.answer()
            return

        if callback.data == 'join':
            phone_number = await queue_manager.phone_exists(user_id)
            if not phone_number:
                await callback.message.edit_text(
                    "Будь ласка, спочатку поділіться номером телефону за допомогою /start.",
                    reply_markup=None
                )
                await callback.message.answer("Поділіться номером:", reply_markup=get_contact_keyboard())
                await callback.answer()
                return
            response = queue_manager.join_queue(user_id, user_name, university_id)
            await queue_manager.save_queue()

        elif callback.data == 'leave':
            response = queue_manager.leave_queue(user_id, university_id)
            await queue_manager.save_queue()

        elif callback.data == 'view':
            response = queue_manager.view_queue(university_id)

        await callback.message.edit_text(response, reply_markup=None)
        await callback.message.answer("Оберіть дію:", reply_markup=await get_main_keyboard(user_id))
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ callback failure {callback.data}: {e}")
        await callback.message.answer("Сталася помилка. Спробуйте ще раз.", reply_markup=await get_main_keyboard(user_id))
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
    try:
        await bot.session.close()
        logger.info("Бот зупинений")
    except Exception as e:
        logger.error(f"Помилка при завершенні роботи бота: {e}")

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
    except (KeyboardInterrupt, SystemExit):
        logger.info("Отримано запит на завершення")
        await shutdown()
    except Exception as e:
        logger.critical(f"❌ Критична помилка: {e}")
        await shutdown()
        raise
    finally:
        await shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Програма завершена")