CREATE DATABASE telegram_queue;
USE telegram_queue;

CREATE TABLE queue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    user_name VARCHAR(255) NOT NULL,
    position INT NOT NULL
);