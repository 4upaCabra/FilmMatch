#!/usr/bin/env python3
"""
Миграция: добавление поля description в таблицу movies.
Запуск: python migrate.py
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import DATABASE_URL
from app.models import Base, Movie

def run_migration():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)

    # Проверяем, существует ли таблица
    if "movies" not in inspector.get_table_names():
        print("Таблица movies не найдена. Создаём все таблицы...")
        Base.metadata.create_all(bind=engine)
        print("Готово!")
        return

    # Проверяем, существует ли колонка description
    columns = [col["name"] for col in inspector.get_columns("movies")]
    if "description" in columns:
        print("Колонка description уже существует.")
        return

    print("Добавляем колонку description в таблицу movies...")
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE movies ADD COLUMN description TEXT"))
        conn.commit()

    print("Миграция успешно выполнена!")


if __name__ == "__main__":
    run_migration()
