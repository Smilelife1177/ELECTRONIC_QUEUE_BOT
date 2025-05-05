import mysql.connector

db_config = {
    'user': 'bot_user',
    'password': '7730130',
    'host': 'localhost',
    'database': 'telegram_queue'
}

try:
    conn = mysql.connector.connect(**db_config)
    print("Підключення успішне!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Таблиці:", tables)
    conn.close()
except mysql.connector.Error as err:
    print(f"Помилка: {err}")