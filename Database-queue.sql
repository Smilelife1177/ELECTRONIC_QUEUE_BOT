-- Drop the user if it exists to avoid conflicts
DROP USER IF EXISTS 'bot_user'@'localhost';

-- Create the user
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY '7730130';

-- Grant privileges on the telegram_queue database
GRANT ALL PRIVILEGES ON telegram_queue.* TO 'bot_user'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS telegram_queue CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE telegram_queue;

-- Create the universities table
DROP TABLE IF EXISTS universities;
CREATE TABLE universities (
    university_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    UNIQUE (name)
);

-- Create the users table with is_admin flag
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create the queue table (removed user_name)
DROP TABLE IF EXISTS queue;
CREATE TABLE queue (
    user_id BIGINT NOT NULL,
    university_id INT NOT NULL,
    join_time DATETIME NOT NULL,
    PRIMARY KEY (user_id, university_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (university_id) REFERENCES universities(university_id) ON DELETE CASCADE
);

-- Create the user_history table (removed user_name)
DROP TABLE IF EXISTS user_history;
CREATE TABLE user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create the broadcast_messages table (removed admin_name)
DROP TABLE IF EXISTS broadcast_messages;
CREATE TABLE broadcast_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    message_text TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Insert distinct Ukrainian universities
INSERT INTO universities (name) VALUES
    ('Київський національний університет імені Тараса Шевченка'),
    ('Національний технічний університет України «Київський політехнічний інститут імені Ігоря Сікорського»'),
    ('Львівський національний університет імені Івана Франка'),
    ('Харківський національний університет імені В. Н. Каразіна'),
    ('Одеський національний університет імені І. І. Мечникова'),
    ('Національний університет «Львівська політехніка»'),
    ('Дніпровський національний університет імені Олеся Гончара'),
    ('Національний авіаційний університет'),
    ('Київський національний економічний університет імені Вадима Гетьмана'),
    ('Чернівецький національний університет імені Юрія Федьковича');

-- Insert sample users with is_admin flag
INSERT INTO users (user_id, user_name, phone_number, is_admin) VALUES
    (967484016, 'Олег', '+380123456789', TRUE),
    (1885828317, 'Максим', '+380987654321', TRUE);