CREATE DATABASE IF NOT EXISTS classroom_hub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'classroomhub_user'@'127.0.0.1' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON classroom_hub.* TO 'classroomhub_user'@'127.0.0.1';
GRANT ALL PRIVILEGES ON test_classroom_hub.* TO 'classroomhub_user'@'127.0.0.1';
FLUSH PRIVILEGES;