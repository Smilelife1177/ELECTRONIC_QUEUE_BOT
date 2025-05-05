CREATE USER IF NOT EXISTS 'bot_user'@'localhost' IDENTIFIED BY '7730130';
GRANT ALL PRIVILEGES ON telegram_queue.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;