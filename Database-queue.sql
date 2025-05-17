CREATE USER IF NOT EXISTS 'bot_user'@'localhost' IDENTIFIED BY '7730130';
GRANT ALL PRIVILEGES ON telegram_queue.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS telegram_queue;
USE telegram_queue;

CREATE TABLE IF NOT EXISTS queue (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    position INT NOT NULL,
    join_time DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255),
    phone_number VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(255),
    action VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);