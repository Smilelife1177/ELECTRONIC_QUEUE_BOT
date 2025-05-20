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

-- Drop and recreate the universities table with a UNIQUE constraint
DROP TABLE IF EXISTS universities;
CREATE TABLE universities (
    university_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    UNIQUE (name)
);

-- Create the queue table
CREATE TABLE IF NOT EXISTS queue (
    user_id BIGINT NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    university_id INT NOT NULL,
    join_time DATETIME NOT NULL,
    PRIMARY KEY (user_id, university_id),
    FOREIGN KEY (university_id) REFERENCES universities(university_id) ON DELETE CASCADE
);

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255),
    phone_number VARCHAR(20)
);

-- Create the user_history table
CREATE TABLE IF NOT EXISTS user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(255),
    action VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the admins table
CREATE TABLE IF NOT EXISTS admins (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255),
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

-- Insert a sample admin (replace with actual admin user_id and user_name)
INSERT INTO admins (user_id, user_name) VALUES
    (967484016, 'Олег');
    (1885828317,'Максим');