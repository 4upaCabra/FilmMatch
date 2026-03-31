# 🎬 FilmMatch

<div align="center">

**Совместный выбор фильмов в стиле Tinder**

Веб-приложение для парного выбора фильмов: свайпайте фильмы, получайте матчи и смотрите вместе.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

<div align="center">
  <img src="screen/filmach1.webp" height="500" alt="FilmMatch интерфейс 1" />
  <img src="screen/filmach2.webp" height="500" alt="FilmMatch интерфейс 2" />
</div>

---

## 🚀 Быстрый старт

```bash
# Запуск через скрипт (рекомендуется)
./start.sh

# Остановка
docker-compose down

# Остановка с очисткой данных
docker-compose down -v
```

> **💡 Доступ к приложению:**
> - 🌐 **Frontend:** http://localhost:3000
> - 🔌 **Backend API:** http://localhost:8001
> - 📚 **API Docs:** http://localhost:8001/docs

## 🛠 Стек

| Компонент | Технологии |
|:----------|:-----------|
| **Frontend** | React 18, Vite, TailwindCSS |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, JWT |
| **База данных** | PostgreSQL 15 |
| **API** | TMDB (постеры, описания) |
| **Контейнеризация** | Docker, Docker Compose |

## 📦 Структура проекта

```
FilmMatch/
├── backend/app/       # FastAPI API
├── frontend/src/      # React компоненты
├── database/init/     # SQL миграции
├── docker-compose.yml
├── .env               # Переменные окружения (не в git)
├── .env.example       # Шаблон переменных
└── start.sh           # Скрипт запуска
```

## 🔑 Переменные окружения

**Скопируйте `.env.example` в `.env` и настройте:**

```bash
cp .env.example .env
```

<details>
<summary><b>📋 Пример .env файла (нажмите для просмотра)</b></summary>

```env
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=SecurePass2024
POSTGRES_DB=movie_matcher
DATABASE_URL=postgresql://user:SecurePass2024@db:5432/movie_matcher

# TMDB API (получите на https://www.themoviedb.org/settings/api)
TMDB_API_KEY=your_api_key_here
TMDB_BEARER_TOKEN=your_bearer_token_here
TMDB_PROXY_URL=  # Оставьте пустым или укажите прокси

# JWT Secret (смените на случайную строку!)
JWT_SECRET=your-secret-key-change-in-production

# Frontend URL (для CORS)
FRONTEND_URL=http://localhost:3000
```

</details>

## 📡 API Endpoints

| Метод | Эндпоинт | Описание |
|:-----:|:---------|:---------|
| `POST` | `/register` | Создать пользователя |
| `POST` | `/login` | Получить JWT токен |
| `GET` | `/movies/next` | Следующий фильм для свайпа |
| `POST` | `/swipe` | Свайп (возвращает `is_match`) |
| `POST` | `/movies/discover` | Загрузить фильмы из TMDB |
| `GET` | `/users/active` | Список активных пользователей |
| `DELETE` | `/users/{user_id}` | Удалить пользователя (завершить сессию) |
| `DELETE` | `/users/me/swipes` | Очистить свайпы текущего пользователя |

## 🧹 Полезные команды

| Команда | Описание |
|---------|----------|
| `./start.sh` | Запуск приложения |
| `docker-compose down -v && ./start.sh` | Пересоздать БД и запустить |
| `curl -X POST http://localhost:8001/movies/discover` | Добавить фильмы вручную |
| `docker-compose logs -f backend` | Логи backend |
| `docker-compose logs -f frontend` | Логи frontend |
| `curl http://localhost:8001/users/active` | Проверка API |

<details>
<summary><b>📝 Подробные команды</b></summary>

```bash
# Запуск (через скрипт)
./start.sh

# Пересоздать БД
docker-compose down -v && ./start.sh

# Добавить фильмы вручную
curl -X POST http://localhost:8001/movies/discover

# Логи
docker-compose logs -f backend
docker-compose logs -f frontend

# Проверка API
curl http://localhost:8001/users/active
```

</details>

## ✨ Особенности

| Функция | Описание |
|---------|----------|
| 🔐 **JWT аутентификация** | Токен хранится в localStorage |
| 💕 **Матчинг** | Уведомление при взаимном лайке |
| 🎭 **Фильтры** | По году, жанрам, просмотренным |
| ⚡ **Ленивая загрузка** | Автоподгрузка фильмов из TMDB при нехватке |
| 👥 **Управление сессиями** | Список активных пользователей с возможностью завершения |

## 🔒 Безопасность

- ✅ Секреты вынесены в `.env` (не в репозитории)
- ✅ JWT токены для аутентификации
- ✅ CORS ограничен до `FRONTEND_URL`
- ✅ SSL проверка для TMDB API
- ✅ Пароль БД без спецсимволов (для совместимости)

---

<div align="center">

**Made with ❤️ for movie lovers**

[Начать использование](#-быстрый-старт) • [Документация API](http://localhost:8001/docs) • [TMDB API](https://www.themoviedb.org/documentation/api)

</div>
