#!/usr/bin/env python3
"""Скрипт миграции БД — создание таблиц и идемпотентное обновление схемы."""
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from app.database import Base, engine
from app import models  # noqa: F401


def run_migrations() -> None:
    print("Running database migrations...")
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        # Идемпотентное обновление существующих томов PostgreSQL
        conn.execute(text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS description TEXT;"))
        conn.execute(text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS tmdb_id INTEGER;"))
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_movies_tmdb_id ON movies (tmdb_id) WHERE tmdb_id IS NOT NULL;")
        )

        # Очистка устаревшей таблицы истории Кинопоиска и технического default_user без активности
        conn.execute(text("DROP TABLE IF EXISTS watch_history;"))
        conn.execute(
            text(
                "DELETE FROM users WHERE username = 'default_user' "
                "AND NOT EXISTS (SELECT 1 FROM swipes WHERE swipes.user_id = users.id);"
            )
        )

        # Удаление возможных старых дублей свайпов перед созданием уникального индекса
        conn.execute(
            text(
                "DELETE FROM swipes a USING swipes b "
                "WHERE a.id < b.id AND a.user_id = b.user_id AND a.movie_id = b.movie_id;"
            )
        )
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_swipes_user_id ON swipes (user_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_swipes_movie_id ON swipes (movie_id);"))
        conn.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_swipes_user_movie ON swipes (user_id, movie_id);")
        )

    print("Database schema is up to date!")


if __name__ == "__main__":
    run_migrations()
