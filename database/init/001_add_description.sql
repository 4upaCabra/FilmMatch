-- Миграция: добавление поля description в таблицу movies
-- Запуск: docker exec movie_matcher_db psql -U user -d movie_matcher -f /docker-entrypoint-initdb.d/001_add_description.sql

ALTER TABLE movies ADD COLUMN IF NOT EXISTS description TEXT;
