import aiosqlite
from collections import deque
from datetime import datetime
import asyncio
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self, db_path="queue.db"):
        self.db_path = db_path
        self.queue = deque()  # Локальна копія черги
        self.user_names = {}  # Кеш імен користувачів
        self.join_times = {}  # Кеш часу входу

    async def startup(self):
        """Виконує асинхронну ініціалізацію під час запуску бота"""
        logger.info("Запуск ініціалізації бази даних")
        await self.init_db()

    async def init_db(self):
        """Ініціалізація бази даних і таблиці"""
        try:
<<<<<<< HEAD
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS queue (
                        user_id INTEGER PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        position INTEGER NOT NULL,
                        join_time TEXT NOT NULL
                    )
                """)
                await db.commit()
                logger.info("База даних ініціалізована")
                await self.load_queue()
        except Exception as e:
            logger.error(f"Помилка ініціалізації бази даних: {e}")
            raise
=======
            logger.info("Спроба підключення до MySQL")
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            logger.info("Підключення до MySQL успішне")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    university_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    UNIQUE (name)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT FALSE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    user_id BIGINT NOT NULL,
                    university_id INT NOT NULL,
                    join_time DATETIME NOT NULL,
                    PRIMARY KEY (user_id, university_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (university_id) REFERENCES universities(university_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    action VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS broadcast_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    admin_id BIGINT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
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

    async def is_admin(self, user_id: int) -> bool:
        """Перевіряє, чи є користувач адміністратором"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result is not None and result[0]
        except mysql.connector.Error as e:
            logger.error(f"Помилка перевірки статусу адміністратора: {e}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def get_universities(self):
        """Отримує список університетів"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT university_id, name FROM universities")
            universities = cursor.fetchall()
            logger.info("Університети успішно завантажені")
            return universities
        except mysql.connector.Error as e:
            logger.error(f"Помилка завантаження університетів: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
>>>>>>> 56dd5f2 (3normalform)

    async def load_queue(self):
        """Завантаження черги з бази даних"""
        self.queue.clear()
        self.user_names.clear()
        self.join_times.clear()
        try:
<<<<<<< HEAD
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT user_id, user_name, join_time FROM queue ORDER BY position") as cursor:
                    async for row in cursor:
                        user_id, user_name, join_time = row
                        self.queue.append(user_id)
                        self.user_names[user_id] = user_name
                        self.join_times[user_id] = datetime.fromisoformat(join_time)
            logger.info("Черга успішно завантажена з бази даних")
        except Exception as e:
            logger.error(f"Помилка завантаження черги: {e}")
=======
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT q.user_id, u.user_name, q.university_id, q.join_time 
                FROM queue q
                JOIN users u ON q.user_id = u.user_id
                ORDER BY q.join_time
            """)
            for row in cursor.fetchall():
                user_id, user_name, university_id, join_time = row
                if university_id not in self.queues:
                    self.queues[university_id] = deque()
                self.queues[university_id].append(user_id)
                self.user_names[(user_id, university_id)] = user_name
                self.join_times[(user_id, university_id)] = join_time
            logger.info("Черги успішно завантажені з бази даних")
        except mysql.connector.Error as e:
            logger.error(f"Помилка завантаження черг: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
>>>>>>> 56dd5f2 (3normalform)

    async def save_queue(self):
        """Збереження черги в базу даних"""
        try:
<<<<<<< HEAD
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM queue")
                for i, user_id in enumerate(self.queue):
                    await db.execute(
                        "INSERT INTO queue (user_id, user_name, position, join_time) VALUES (?, ?, ?, ?)",
                        (user_id, self.user_names[user_id], i + 1, self.join_times[user_id].isoformat())
=======
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM queue")
            for university_id, queue in self.queues.items():
                for user_id in queue:
                    cursor.execute(
                        "INSERT INTO queue (user_id, university_id, join_time) VALUES (%s, %s, %s)",
                        (user_id, university_id, self.join_times[(user_id, university_id)])
>>>>>>> 56dd5f2 (3normalform)
                    )
                await db.commit()
                logger.info("Черга успішно збережена в базі даних")
        except Exception as e:
            logger.error(f"Помилка збереження черги: {e}")

<<<<<<< HEAD
    def join_queue(self, user_id: int, user_name: str) -> str:
        """Додає користувача до черги"""
        if user_id not in self.queue:
            self.queue.append(user_id)
            self.user_names[user_id] = user_name
            self.join_times[user_id] = datetime.now()
            logger.info(f"Користувач {user_name} (ID: {user_id}) доданий до черги")
            return f"{user_name}, ви додані до черги. Ваш номер: {len(self.queue)}"
        logger.warning(f"Користувач {user_name} (ID: {user_id}) вже в черзі")
        return "Ви вже в черзі!"
=======
    async def save_user_phone(self, user_id: int, user_name: str, phone_number: str):
        """Збереження номера телефону користувача"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, user_name, phone_number, is_admin) VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE user_name=%s, phone_number=%s",
                (user_id, user_name, phone_number, False, user_name, phone_number)
            )
            conn.commit()
            logger.info(f"Збережено номер: {phone_number} для {user_name} (ID: {user_id})")
        except mysql.connector.Error as e:
            logger.error(f"Помилка збереження номера телефону: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
>>>>>>> 56dd5f2 (3normalform)

    def leave_queue(self, user_id: int) -> str:
        """Видаляє користувача з черги"""
        if user_id in self.queue:
            self.queue.remove(user_id)
            user_name = self.user_names.pop(user_id)
            self.join_times.pop(user_id)
            logger.info(f"Користувач {user_name} (ID: {user_id}) покинув чергу")
            return f"{user_name}, ви покинули чергу."
        logger.warning(f"Користувач (ID: {user_id}) не в черзі")
        return "Вас немає в черзі!"

<<<<<<< HEAD
    def view_queue(self) -> str:
        """Повертає список учасників черги"""
        if not self.queue:
            logger.info("Черга порожня")
=======
    async def log_action(self, user_id: int, user_name: str, action: str):
        """Запис дії в історію"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_history (user_id, action) VALUES (%s, %s)",
                (user_id, action)
            )
            conn.commit()
            logger.info(f"Дія записана: {action} для {user_name} (ID: {user_id})")
        except mysql.connector.Error as e:
            logger.error(f"Помилка запису історії: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def get_user_history(self, user_id: int) -> str:
        """Повертає історію дій користувача (доступно лише для адмінів)"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_name, h.action, h.timestamp 
                FROM user_history h
                JOIN users u ON h.user_id = u.user_id
                WHERE h.user_id = %s 
                ORDER BY h.timestamp DESC
            """, (user_id,))
            history = cursor.fetchall()
            if not history:
                return "Історія дій порожня."
            result = ["📜 Історія дій:"]
            for user_name, action, timestamp in history:
                result.append(f"[{timestamp}] {user_name}: {action}")
            return "\n".join(result)
        except mysql.connector.Error as e:
            logger.error(f"Помилка отримання історії користувача: {e}")
            return "Помилка при отриманні історії."
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    async def broadcast_message(self, bot, admin_id: int, admin_name: str, message_text: str):
        """Зберігає повідомлення в базу даних і надсилає його всім користувачам"""
        try:
            # Збереження повідомлення в базу даних
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO broadcast_messages (admin_id, message_text) VALUES (%s, %s)",
                (admin_id, message_text)
            )
            conn.commit()
            logger.info(f"Оголошення збережено від {admin_name} (ID: {admin_id})")

            # Логування дії
            await self.log_action(admin_id, admin_name, f"broadcast_message: {message_text[:50]}...")

            # Отримання всіх користувачів
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()
            logger.info(f"Надсилання оголошення {len(users)} користувачам")

            # Форматування повідомлення
            broadcast_text = f"📢 Оголошення від адміністратора {admin_name}:\n{message_text}"

            # Надсилання повідомлення кожному користувачу
            for (user_id,) in users:
                try:
                    await bot.send_message(chat_id=user_id, text=broadcast_text)
                    logger.info(f"Оголошення надіслано користувачу {user_id}")
                except Exception as e:
                    logger.error(f"Помилка надсилання оголошення користувачу {user_id}: {e}")
                    continue

        except mysql.connector.Error as e:
            logger.error(f"Помилка збереження оголошення: {e}")
            raise
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def join_queue(self, user_id: int, user_name: str, university_id: int) -> str:
        """Додає користувача до черги університету"""
        if university_id not in self.queues:
            self.queues[university_id] = deque()
        queue = self.queues[university_id]
        if user_id not in queue:
            queue.append(user_id)
            self.user_names[(user_id, university_id)] = user_name
            self.join_times[(user_id, university_id)] = datetime.now()
            asyncio.create_task(self.log_action(user_id, user_name, f"join_queue_university_{university_id}"))
            return f"{user_name}, ви додані до черги університету. Ваш номер: {len(queue)}"
        return "Ви вже в черзі цього університету!"

    def leave_queue(self, user_id: int, university_id: int) -> str:
        """Видаляє користувача з черги університету"""
        if university_id not in self.queues or user_id not in self.queues[university_id]:
            logger.warning(f"Користувач (ID: {user_id}) не в черзі університету {university_id}")
            return "Вас немає в черзі цього університету!"
        self.queues[university_id].remove(user_id)
        user_name = self.user_names.pop((user_id, university_id))
        self.join_times.pop((user_id, university_id))
        if not self.queues[university_id]:
            del self.queues[university_id]
        logger.info(f"Користувач {user_name} (ID: {user_id}) покинув чергу університету {university_id}")
        asyncio.create_task(self.log_action(user_id, user_name, f"leave_queue_university_{university_id}"))
        return f"{user_name}, ви покинули чергу університету."

    def view_queue(self, university_id: int) -> str:
        """Повертає список учасників черги університету в рамці"""
        if university_id not in self.queues or not self.queues[university_id]:
            logger.info(f"Черга для університету {university_id} порожня")
>>>>>>> 56dd5f2 (3normalform)
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