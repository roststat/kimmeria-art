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
