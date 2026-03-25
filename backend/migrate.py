#!/usr/bin/env python3
"""Скрипт миграции БД - создание таблиц."""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import engine, Base
from app import models

def run_migrations():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    run_migrations()
