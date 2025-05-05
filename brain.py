import mysql.connector
from collections import deque
from datetime import datetime
import asyncio
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, db_config):
        self.db_config = db_config
        logger.info(f"Ініціалізація QueueManager з db_config: {db_config}")
        self.queue = deque()  # Локальна копія черги
        self.user_names = {}  # Кеш імен користувачів
        self.join_times = {}  # Кеш часу входу

    async def startup(self):
        """Виконує ініціалізацію під час запуску бота"""
        logger.info("Запуск ініціалізації бази даних")
        await self.init_db()

    async def init_db(self):
        """Ініціалізація бази даних і таблиць"""
        try:
            logger.info("Спроба підключення до MySQL")
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            logger.info("Підключення до MySQL успішне")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    user_id BIGINT PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    position INT NOT NULL,
                    join_time DATETIME NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    user_name VARCHAR(255),
                    phone_number VARCHAR(20)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    user_name VARCHAR(255),
                    action VARCHAR(255),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("База даних ініціалізована")
            await self.load_queue()
        except mysql.connector.Error as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            raise
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def clear_queue(self):
        """Очищає таблицю queue, залишаючи user_history і users недоторканими"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM queue")
            conn.commit()
            self.queue.clear()
            self.user_names.clear()
            self.join_times.clear()
            # Перевірка, чи таблиця порожня
            cursor.execute("SELECT COUNT(*) FROM queue")
            count = cursor.fetchone()[0]
            if count == 0:
                logger.info("Таблиця queue успішно очищена")
            else:
                logger.warning(f"Таблиця queue не очищена, залишилося {count} записів")
        except mysql.connector.Error as e:
            logger.error(f"Помилка очищення таблиці queue: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def load_queue(self):
        """Завантаження черги з бази даних"""
        self.queue.clear()
        self.user_names.clear()
        self.join_times.clear()
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, user_name, join_time FROM queue ORDER BY position")
            for row in cursor.fetchall():
                user_id, user_name, join_time = row
                self.queue.append(user_id)
                self.user_names[user_id] = user_name
                self.join_times[user_id] = join_time
            logger.info("Черга успішно завантажена з бази даних")
        except mysql.connector.Error as e:
            logger.error(f"Помилка завантаження черги: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def save_queue(self):
        """Збереження черги в базу даних"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM queue")
            for i, user_id in enumerate(self.queue):
                cursor.execute(
                    "INSERT INTO queue (user_id, user_name, position, join_time) VALUES (%s, %s, %s, %s)",
                    (user_id, self.user_names[user_id], i + 1, self.join_times[user_id])
                )
            conn.commit()
            logger.info("Черга успішно збережена в базі даних")
        except mysql.connector.Error as e:
            logger.error(f"Помилка збереження черги: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def save_user_phone(self, user_id: int, user_name: str, phone_number: str):
        """Збереження номера телефону користувача"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, user_name, phone_number) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE user_name=%s, phone_number=%s",
                (user_id, user_name, phone_number, user_name, phone_number)
            )
            conn.commit()
            logger.info(f"Збережено номер: {phone_number} для {user_name} (ID: {user_id})")
        except mysql.connector.Error as e:
            logger.error(f"Помилка збереження номера телефону: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def phone_exists(self, user_id: int) -> str:
        """Перевірка, чи існує номер телефону для користувача"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as e:
            logger.error(f"Помилка перевірки номера телефону: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def log_action(self, user_id: int, user_name: str, action: str):
        """Запис дії в історію"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_history (user_id, user_name, action) VALUES (%s, %s, %s)",
                (user_id, user_name, action)
            )
            conn.commit()
            logger.info(f"Дія записана: {action} для {user_name} (ID: {user_id})")
        except mysql.connector.Error as e:
            logger.error(f"Помилка запису історії: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def join_queue(self, user_id: int, user_name: str) -> str:
        """Додає користувача до черги"""
        if user_id not in self.queue:
            self.queue.append(user_id)
            self.user_names[user_id] = user_name
            self.join_times[user_id] = datetime.now()
            logger.info(f"Користувач {user_name} (ID: {user_id}) доданий до черги")
            asyncio.create_task(self.log_action(user_id, user_name, "join_queue"))
            return f"{user_name}, ви додані до черги. Ваш номер: {len(self.queue)}"
        logger.warning(f"Користувач {user_name} (ID: {user_id}) вже в черзі")
        return "Ви вже в черзі!"

    def leave_queue(self, user_id: int) -> str:
        """Видаляє користувача з черги"""
        if user_id in self.queue:
            self.queue.remove(user_id)
            user_name = self.user_names.pop(user_id)
            self.join_times.pop(user_id)
            logger.info(f"Користувач {user_name} (ID: {user_id}) покинув чергу")
            asyncio.create_task(self.log_action(user_id, user_name, "leave_queue"))
            return f"{user_name}, ви покинули чергу."
        logger.warning(f"Користувач (ID: {user_id}) не в черзі")
        return "Вас немає в черзі!"

    def view_queue(self) -> str:
        """Повертає список учасників черги"""
        if not self.queue:
            logger.info("Черга порожня")
            return "Черга порожня."
        queue_list = "\n".join(f"{i+1}. {self.user_names[uid]}" for i, uid in enumerate(self.queue))
        logger.info("Запит на перегляд черги")
        return f"Поточна черга:\n{queue_list}"

    async def next_in_queue(self) -> tuple[str, list[int]]:
        """Викликає наступного користувача та повертає оновлені позиції"""
        if not self.queue:
            logger.info("Черга порожня при виклику наступного")
            return "Черга порожня.", []
        next_user = self.queue.popleft()
        next_name = self.user_names.pop(next_user)
        self.join_times.pop(next_user)
        updated_users = list(self.queue)
        logger.info(f"Наступний користувач: {next_name} (ID: {next_user})")
        await self.log_action(next_user, next_name, "next_in_queue")
        return f"Наступний: {next_name}", updated_users

    async def notify_position(self, user_id: int) -> str:
        """Повертає повідомлення про поточну позицію користувача"""
        if user_id not in self.queue:
            logger.warning(f"Користувач (ID: {user_id}) не в черзі для сповіщення")
            return "Вас немає в черзі!"
        position = list(self.queue).index(user_id) + 1
        logger.info(f"Сповіщення позиції для {self.user_names[user_id]} (ID: {user_id}): {position}")
        return f"{self.user_names[user_id]}, ваша позиція в черзі: {position}"

    async def remind_first(self, bot, chat_id: int):
        """Нагадує першому користувачу через 1 хвилину"""
        if not self.queue:
            logger.info("Черга порожня, нагадування не потрібне")
            return
        await asyncio.sleep(60)
        if self.queue:
            first_user = self.queue[0]
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f"{self.user_names[first_user]}, ви перший у черзі! Будь ласка, підготуйтеся."
                )
                logger.info(f"Нагадування надіслано першому користувачу (ID: {first_user})")
            except Exception as e:
                logger.error(f"Помилка надсилання нагадування: {e}")

    def get_stats(self) -> str:
        """Повертає статистику черги"""
        if not self.queue:
            logger.info("Черга порожня, статистика недоступна")
            return "Черга порожня, немає даних для статистики."
        total_users = len(self.queue)
        avg_wait = sum((datetime.now() - self.join_times[uid]).total_seconds() / 60 
                       for uid in self.queue) / total_users if total_users else 0
        logger.info(f"Запит статистики: {total_users} користувачів, середній час очікування {avg_wait:.1f} хвилин")
        return (f"📊 Статистика черги:\n"
                f"Кількість учасників: {total_users}\n"
                f"Середній час очікування: {avg_wait:.1f} хвилин")