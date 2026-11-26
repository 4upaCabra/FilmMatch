#!/bin/bash
# Скрипт запуска FilmMatch
set -e

if [ ! -f .env ]; then
  echo "❌ Файл .env не найден. Создайте его на основе шаблона: cp .env.example .env"
  exit 1
fi

set -a
source .env
set +a

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "❌ Docker Compose не установлен."
  exit 1
fi

$COMPOSE_CMD up -d --build

echo ""
echo "✅ FilmMatch запущен!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
