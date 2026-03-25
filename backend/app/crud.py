from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from . import models, schemas, tmdb
import pandas as pd
from datetime import datetime
from typing import Optional
import asyncio

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_or_create_user(db: Session, username: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        db_user = models.User(username=username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Check if user has uploaded watch history
    has_history = db.query(models.WatchHistory).filter(models.WatchHistory.user_id == db_user.id).first() is not None
    
    # Return a dict that matches UserResponse schema
    return {
        "id": db_user.id,
        "username": db_user.username,
        "has_history": has_history
    }

def create_swipe(db: Session, swipe_data: dict):
    # Check if this user already swiped this movie
    db_swipe = db.query(models.Swipe).filter(
        models.Swipe.user_id == swipe_data["user_id"],
        models.Swipe.movie_id == swipe_data["movie_id"]
    ).first()

    if db_swipe:
        db_swipe.is_liked = swipe_data["is_liked"]
        db_swipe.created_at = datetime.utcnow()
    else:
        db_swipe = models.Swipe(**swipe_data)
        db.add(db_swipe)

    db.commit()
    db.refresh(db_swipe)

    # Check for match IF user liked the movie
    is_match = False
    movie = None
    if db_swipe.is_liked:
        # Search for OTHER users who liked the SAME movie
        other_like = db.query(models.Swipe).filter(
            models.Swipe.movie_id == db_swipe.movie_id,
            models.Swipe.user_id != db_swipe.user_id,
            models.Swipe.is_liked == True
        ).first()

        if other_like:
            is_match = True
            movie = db.query(models.Movie).filter(models.Movie.id == db_swipe.movie_id).first()

    # Return dict with match info
    return {
        "id": db_swipe.id,
        "user_id": db_swipe.user_id,
        "movie_id": db_swipe.movie_id,
        "is_liked": db_swipe.is_liked,
        "created_at": db_swipe.created_at,
        "is_match": is_match,
        "movie": movie
    }

async def populate_discover_movies(db: Session, page: int = 1):
    """Fetch movies from multiple TMDB sources and add to DB."""
    # Fetch genre mapping
    genre_map = await tmdb.fetch_genres()

    # Fetch from sources with released movies only (no upcoming)
    top_rated = await tmdb.fetch_top_rated_movies(page=page)
    now_playing = await tmdb.fetch_now_playing_movies(page=page)
    popular = await tmdb.fetch_popular_movies(page=page)
    trending = await tmdb.fetch_trending_movies(page=page)

    # Combine all results (may have duplicates, handled below)
    all_results = top_rated + now_playing + popular + trending
    added_count = 0

    for item in all_results:
        title = item.get("title")
        if not title:
            continue

        # Extract year from release_date "YYYY-MM-DD"
        release_date = item.get("release_date", "")
        year = None
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except ValueError:
                pass

        # Get genre names from IDs
        genre_ids = item.get("genre_ids", [])
        genre_names = [genre_map.get(gid).lower() for gid in genre_ids if genre_map.get(gid)]

        # Check if exists
        exists = db.query(models.Movie).filter(models.Movie.title == title).first()
        if not exists:
            poster_path = item.get("poster_path")
            poster_url = f"{tmdb.TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None

            movie = models.Movie(
                title=title,
                year=year,
                genres=genre_names,
                poster_url=poster_url,
                rating=item.get("vote_average"),
                description=item.get("overview")
            )
            db.add(movie)
            added_count += 1
        elif not exists.genres and genre_names:
            # Update existing movie if genres were missing
            exists.genres = genre_names

    if added_count > 0:
        db.commit()
    return added_count


async def get_next_movie(db: Session, user_id: int, exclude_watched: bool = False, min_year: Optional[int] = None, genre: Optional[str] = None) -> Optional[models.Movie]:
    query = db.query(models.Movie)

    # Всегда исключаем фильмы, которые пользователь уже свайпнул
    swiped_subquery = db.query(models.Swipe.movie_id).filter(models.Swipe.user_id == user_id)
    query = query.filter(~models.Movie.id.in_(swiped_subquery))

    # Дополнительно исключаем просмотренные, если включена опция
    if exclude_watched:
        watched_subquery = db.query(models.WatchHistory.movie_id).filter(models.WatchHistory.user_id == user_id)
        query = query.filter(~models.Movie.id.in_(watched_subquery))

    if min_year:
        query = query.filter(models.Movie.year >= min_year)

    if genre:
        # Support both single string and list of genres
        from sqlalchemy import or_
        if isinstance(genre, str):
            genres_list = [genre]
        else:
            genres_list = genre

        if genres_list:
            # Lowercase for case-insensitive matching
            genres_list = [g.lower() for g in genres_list]
            genre_filters = [models.Movie.genres.any(g) for g in genres_list]
            query = query.filter(or_(*genre_filters))

    # Получаем текущий фильм
    movie = query.order_by(func.random()).first()

    # Предзагрузка: если фильмов в пуле мало (< 20), запускаем загрузку новых
    # но не блокируем возврат текущего фильма
    count = query.count()
    if count < 20:
        # Загружаем 10 страниц асинхронно (не блокируя ответ) ~500 фильмов
        from .database import SessionLocal
        asyncio.create_task(populate_discover_batch(pages=10, db_session=SessionLocal))

    # Lazily fetch poster if it's missing (though populate_discover_movies should have it)
    if movie and not movie.poster_url:
        poster_url = await tmdb.fetch_poster_url(movie.title, movie.year)
        if poster_url:
            movie.poster_url = poster_url
            db.commit()
            db.refresh(movie)

    return movie


async def populate_discover_batch(pages: int = 5, db_session=None):
    """Загрузить несколько страниц фильмов из TMDB в фоне."""
    db = db_session()
    try:
        for page in range(1, pages + 1):
            await populate_discover_movies(db, page=page)
        db.commit()
    except Exception as e:
        print(f"[CRUD] Error in background discover batch: {e}")
        db.rollback()
    finally:
        db.close()

def clear_user_swipes(db: Session, user_id: int):
    db.query(models.Swipe).filter(models.Swipe.user_id == user_id).delete()
    db.commit()

def get_active_users(db: Session):
    # Возвращаем всех пользователей (активные сессии)
    return db.query(models.User).all()


def delete_user(db: Session, user_id: int):
    """Удалить пользователя и все его данные (свайпы, историю)."""
    # Удаляем свайпы
    db.query(models.Swipe).filter(models.Swipe.user_id == user_id).delete()
    # Удаляем историю просмотров
    db.query(models.WatchHistory).filter(models.WatchHistory.user_id == user_id).delete()
    # Удаляем пользователя
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
