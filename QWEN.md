# TinderFilm — Проект приложения для совместного выбора фильмов

## Обзор проекта

**TinderFilm** — это веб-приложение для совместного выбора фильмов в стиле Tinder. Пользователи могут просматривать фильмы, свайпать их (лайк/дизлайк), и получать матчи, когда оба пользователя выбрали один и тот же фильм.

### Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│ PostgreSQL  │
│  (React)    │◀────│  (FastAPI)  │◀────│   (DB)      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │                   │
       ▼                   ▼
  nginx:80           TMDB API
  (Docker)         (постеры, описания)
```

### Технологический стек

| Компонент | Технологии |
|-----------|-----------|
| **Frontend** | React 18, Vite, TailwindCSS, Axios |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| **База данных** | PostgreSQL 15 |
| **Контейнеризация** | Docker, Docker Compose |
| **Внешние API** | TMDB (постеры, описания, метаданные) |

### Структура проекта

```
TinderFilm/
├── backend/
│   ├── app/
│   │   ├── main.py          # Точки входа API (FastAPI)
│   │   ├── models.py        # SQLAlchemy модели
│   │   ├── schemas.py       # Pydantic схемы
│   │   ├── crud.py          # Бизнес-логика и доступ к БД
│   │   ├── database.py      # Подключение к БД
│   │   └── tmdb.py          # Клиент для TMDB API
│   ├── Dockerfile
│   ├── migrate.py           # Скрипт миграции БД
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Корневой компонент
│   │   ├── main.jsx         # Точка входа React
│   │   ├── index.css        # Глобальные стили
│   │   ├── api/
│   │   │   └── client.js    # API клиент (axios)
│   │   └── components/
│   │       ├── LoginScreen.jsx      # Экран входа
│   │       ├── SwipeScreen.jsx      # Экран свайпов
│   │       └── MovieCard.jsx        # Карточка фильма
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── database/
│   └── init/
│       ├── init.sql                 # Инициализация БД
│       └── 001_add_description.sql  # Миграция: поле description
├── docker-compose.yml
└── README.md
```

### Модели данных

**users** — пользователи
- `id`, `username`

**movies** — каталог фильмов
- `id`, `title`, `year`, `genres[]`, `tags[]`, `rating`, `poster_url`, `description`

**watch_history** — история просмотров
- `id`, `user_id`, `movie_id`, `user_rating`, `watched_at`

**swipes** — свайпы пользователей
- `id`, `user_id`, `movie_id`, `is_liked`, `created_at`

---

## Запуск и разработка

### Требования

- Docker и Docker Compose
- Node.js 18+ (для локальной разработки frontend)
- Python 3.11+ (для локальной разработки backend)

### Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка и удаление данных
docker-compose down -v
```

### Доступные эндпоинты

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:3000 | Веб-интерфейс |
| Backend API | http://localhost:8001 | REST API |
| PostgreSQL | localhost:5432 | База данных |
| API Docs | http://localhost:8001/docs | Swagger UI |

### Переменные окружения

**Backend:**
```env
DATABASE_URL=postgresql://user:YOUR_DB_PASSWORD@127.0.0.1:5432/movie_matcher
TMDB_API_KEY=YOUR_TMDB_API_KEY
TMDB_BEARER_TOKEN=YOUR_TMDB_BEARER_TOKEN
```

---

## API Endpoints

### Пользователи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/users` | Создать/получить пользователя |
| `GET` | `/users/active` | Получить активных пользователей |
| `DELETE` | `/users/{user_id}/swipes` | Очистить свайпы пользователя |

### Фильмы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/movies/next` | Получить следующий фильм для свайпа |
| `POST` | `/movies/discover` | Загрузить новые фильмы из TMDB |

### Свайпы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/swipe` | Создать свайп (возвращает `is_match`) |

---

## Миграции базы данных

### Добавление нового поля

Для существующей БД выполните:

```bash
docker exec movie_matcher_db psql -U user -d movie_matcher -c "ALTER TABLE movies ADD COLUMN IF NOT EXISTS description TEXT;"
```

Или используйте файл миграции:
```sql
-- database/init/001_add_description.sql
ALTER TABLE movies ADD COLUMN IF NOT EXISTS description TEXT;
```

---

## Разработка

### Frontend

```bash
cd frontend
npm install
npm run dev        # Запуск dev-сервера
npm run build      # Сборка для продакшена
npm run lint       # Проверка кода
```

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

---

## Особенности реализации

### Логика выбора фильмов

1. **Исключение свайпнутых** — уже оценённые фильмы не предлагаются повторно
2. **Фильтры** — по году выпуска ("свежесть"), жанрам, просмотренным
3. **Ленивая загрузка** — при нехватке фильмов (< 20) автоматически загружаются новые из TMDB (до 10 страниц ~500 фильмов)
4. **Матчинг** — при взаимном лайке показывается уведомление "Это матч!"

### Фронтенд

- **Pending-фильтры** — изменения применяются только после нажатия "Применить фильтры"
- **Описание фильмов** — обрезается по последнему полному предложению
- **Адаптивный UI** — TailwindCSS с тёмной темой
- **Сохранение сессии** — данные пользователя сохраняются в localStorage

### Бэкенд

- **Async/await** — асинхронные запросы к TMDB
- **SQLAlchemy ORM** — работа с БД через сессии
- **Pydantic v2** — валидация данных с `model_dump()`
- **Фоновая загрузка** — `populate_discover_batch` загружает фильмы в фоне

### TMDB интеграция

- **Источники фильмов:** Top Rated, Now Playing, Popular, Trending
- **Изображения:** базовый URL `https://image.tmdb.org/t/p/w500`
- **Жанры:** динамическая подгрузка маппинга жанров

---

## Известные ограничения

- TMDB API требует прокси (настроен в `tmdb.py`)
- Frontend использует `network_mode: host` для backend (localhost:8001)
- CORS разрешён для всех источников (`allow_origins=["*"]`)
- Базовая настройка CORS может быть небезопасна для продакшена

---

## Команды для разработки

### Сброс состояния

```bash
# Очистить свайпы пользователя
docker exec movie_matcher_api python -c "from app.database import SessionLocal; from app import crud; db = SessionLocal(); crud.clear_user_swipes(db, 1); db.close()"

# Пересоздать БД
docker-compose down -v && docker-compose up --build
```

### Добавление фильмов вручную

```bash
# Через API
curl -X POST http://localhost:8001/movies/discover
```

### Просмотр логов

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```
