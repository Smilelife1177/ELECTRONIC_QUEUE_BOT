CREATE TABLE queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(255),
    position INT
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(255)
);

CREATE TABLE user_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    user_name VARCHAR(255),
    action VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    user_name VARCHAR(255),
    phone_number VARCHAR(20)
);

GRANT ALL PRIVILEGES ON telegram_queue.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;

SHOW GRANTS FOR 'bot_user'@'localhost';
ALTER USER 'bot_user'@'localhost' IDENTIFIED BY '7730130';
FLUSH PRIVILEGES;
ALTER TABLE users
ADD COLUMN user_name VARCHAR(255);

ALTER TABLE users
ADD COLUMN phone_number VARCHAR(20);
