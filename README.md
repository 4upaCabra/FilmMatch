# TinderFilm — Совместный выбор фильмов в стиле Tinder

Веб-приложение для парного выбора фильмов: свайпайте фильмы, получайте матчи и смотрите вместе.

## 🚀 Быстрый старт

```bash
# Запуск всех сервисов
docker-compose up --build

# Остановка с очисткой данных
docker-compose down -v
```

**Доступ:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 🛠 Стек

| Компонент | Технологии |
|-----------|-----------|
| Frontend | React 18, Vite, TailwindCSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy |
| БД | PostgreSQL 15 |
| API | TMDB (постеры, описания) |

## 📦 Структура

```
TinderFilm/
├── backend/app/       # FastAPI API
├── frontend/src/      # React компоненты
├── database/init/     # SQL миграции
└── docker-compose.yml
```

## 🔑 Переменные окружения

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:YOUR_DB_PASSWORD@127.0.0.1:5432/movie_matcher
TMDB_API_KEY=YOUR_TMDB_API_KEY
TMDB_BEARER_TOKEN=eyJhbGciOiJIUzI1NiJ9...
```

## 📡 API Endpoints

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/users` | Создать/получить пользователя |
| `GET` | `/movies/next` | Следующий фильм для свайпа |
| `POST` | `/swipe` | Свайп (возвращает `is_match`) |
| `POST` | `/movies/discover` | Загрузить фильмы из TMDB |

## 🧹 Полезные команды

```bash
# Пересоздать БД
docker-compose down -v && docker-compose up --build

# Очистить свайпы пользователя (ID=1)
docker exec movie_matcher_api python -c "from app.database import SessionLocal; from app import crud; db = SessionLocal(); crud.clear_user_swipes(db, 1); db.close()"

# Добавить фильмы вручную
curl -X POST http://localhost:8001/movies/discover

# Логи
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📝 Особенности

- **Матчинг** — уведомление при взаимном лайке
- **Фильтры** — по году, жанрам, просмотренным
- **Ленивая загрузка** — автоподгрузка фильмов из TMDB при нехватке
