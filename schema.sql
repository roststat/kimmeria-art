-- Организаторы (клиенты которые добавляют мероприятия)
CREATE TABLE IF NOT EXISTS users (
  id          SERIAL PRIMARY KEY,
  email       TEXT UNIQUE NOT NULL,
  password    TEXT NOT NULL,           -- bcrypt hash
  name        TEXT NOT NULL,           -- название организации или имя
  phone       TEXT,
  status      TEXT NOT NULL DEFAULT 'active', -- active / blocked
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Мероприятия
CREATE TABLE IF NOT EXISTS events (
  id            SERIAL PRIMARY KEY,
  slug          TEXT UNIQUE NOT NULL,  -- ryba, lecture-afrodita и т.д.
  user_id       INTEGER REFERENCES users(id), -- NULL = добавлено вами вручную
  status        TEXT NOT NULL DEFAULT 'pending', -- pending / published / rejected

  -- Основные поля
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,         -- краткое для карточки
  description_full TEXT,               -- полное для страницы
  date          DATE NOT NULL,
  time          TEXT NOT NULL,         -- "19:00"
  date_label    TEXT NOT NULL,         -- "20 апреля · 19:00"
  format        TEXT NOT NULL,         -- кинопоказ / лекция / спектакль / выставка
  location      TEXT NOT NULL,
  price         TEXT NOT NULL,         -- "800 ₽" или "Свободный вход"
  price_members TEXT,                  -- "500 ₽ членам клуба"
  image_url     TEXT NOT NULL,
  age           TEXT,                  -- "12+", "16+"
  ticket_url    TEXT,                  -- ссылка на билеты

  -- Необязательные поля страницы
  director      TEXT,
  country_year  TEXT,
  cast_list     TEXT,
  host          TEXT,                  -- ведущий
  included      TEXT,                  -- что включено
  og_description TEXT,                 -- для соцсетей

  -- Источник (старые = legacy, новые от организаторов = cabinet)
  source        TEXT NOT NULL DEFAULT 'cabinet',

  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS events_status_date ON events(status, date);
CREATE INDEX IF NOT EXISTS events_slug ON events(slug);
CREATE INDEX IF NOT EXISTS events_user_id ON events(user_id);

-- Расписания заказчиков
CREATE TABLE IF NOT EXISTS schedules (
  id          SERIAL PRIMARY KEY,
  token       TEXT UNIQUE NOT NULL,       -- уникальный токен для виджета
  title       TEXT NOT NULL,              -- "Отель Таврида — май 2026"
  client_name TEXT NOT NULL,              -- имя заказчика
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Программы в расписании заказчика
CREATE TABLE IF NOT EXISTS schedule_items (
  id          SERIAL PRIMARY KEY,
  schedule_id INTEGER NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
  program_slug TEXT NOT NULL,             -- slug из /programmy/ (ryba, kantiya и т.д.)
  program_title TEXT NOT NULL,            -- название (денормализовано для скорости)
  program_image TEXT NOT NULL,            -- картинка
  event_date  DATE NOT NULL,
  event_time  TEXT NOT NULL DEFAULT '19:00',
  price       TEXT NOT NULL DEFAULT 'По запросу',
  sort_order  INTEGER NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS schedule_items_schedule_id ON schedule_items(schedule_id);
CREATE INDEX IF NOT EXISTS schedules_token ON schedules(token);
