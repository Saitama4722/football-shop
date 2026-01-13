-- Проверка существования таблиц
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';

-- Проверка ENUM-типов
SELECT unnest(enum_range(NULL::role)) AS roles;
SELECT unnest(enum_range(NULL::order_status)) AS order_statuses;

-- Тестовая вставка данных
INSERT INTO users (user_id, email, password_hash, role)
VALUES (gen_random_uuid(), 'test@example.com', 'hash123', 'CUSTOMER');

-- Проверка вставки
SELECT COUNT(*)
FROM users
WHERE email = 'test@example.com';
