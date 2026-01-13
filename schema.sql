-- === Enums ===
CREATE TYPE role AS ENUM ('ADMIN', 'DRIVER', 'CUSTOMER');

CREATE TYPE order_status AS ENUM (
  'СОЗДАН',
  'ОЖИДАНИЕ_ОПЛАТЫ',
  'ОПЛАЧЕН',
  'В_ОБРАБОТКЕ',
  'ГОТОВ_К_ОТПРАВКЕ',
  'В_ДОСТАВКЕ',
  'ДОСТАВЛЕН',
  'ОТМЕНЕН'
);

-- === Users ===
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  phone VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  role role NOT NULL
);
