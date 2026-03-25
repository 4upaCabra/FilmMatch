-- Таблица пользователей (локальные аккаунты для совместного выбора)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL
);

-- Таблица всех доступных фильмов (локальный каталог)
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    kp_id INTEGER UNIQUE, -- ID Кинопоиска для синхронизации
    title TEXT NOT NULL,
    year INTEGER,
    genres TEXT[], -- Массив жанров
    tags TEXT[],   -- Массив тегов
    rating FLOAT,
    poster_url TEXT,
    description TEXT
);

-- История просмотров (загруженная из CSV Кинопоиска)
CREATE TABLE watch_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    movie_id INTEGER REFERENCES movies(id),
    user_rating INTEGER,
    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);

-- Таблица "Лайков" для матчинга в реальном времени
CREATE TABLE swipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    movie_id INTEGER REFERENCES movies(id),
    is_liked BOOLEAN, -- TRUE = лайк, FALSE = дизлайк
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a default user
INSERT INTO users (username) VALUES ('default_user');
