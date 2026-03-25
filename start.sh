#!/bin/bash
# Скрипт запуска TinderFilm
# Очищает переменные окружения и запускает с .env файлом

set -a  # Автоматически экспортировать все переменные
source .env
set +a  # Выключить автоматический экспорт

# Запуск сервисов
docker-compose up -d --build

echo ""
echo "✅ TinderFilm запущен!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
