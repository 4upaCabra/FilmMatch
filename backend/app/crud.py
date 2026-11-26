import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Union

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, tmdb

_background_discover_running = False


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_or_create_user(db: Session, username: str) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        db_user = models.User(username=username)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user


def create_swipe(db: Session, swipe_data: dict) -> dict:
    db_swipe = db.query(models.Swipe).filter(
        models.Swipe.user_id == swipe_data["user_id"],
        models.Swipe.movie_id == swipe_data["movie_id"],
    ).first()

    if db_swipe:
        db_swipe.is_liked = swipe_data["is_liked"]
        db_swipe.created_at = datetime.now(timezone.utc)
    else:
        db_swipe = models.Swipe(**swipe_data)
        db.add(db_swipe)

    db.commit()
    db.refresh(db_swipe)

    is_match = False
    movie = None
    if db_swipe.is_liked:
        other_like = db.query(models.Swipe).filter(
            models.Swipe.movie_id == db_swipe.movie_id,
            models.Swipe.user_id != db_swipe.user_id,
            models.Swipe.is_liked.is_(True),
        ).first()

        if other_like:
            is_match = True
            movie = db.query(models.Movie).filter(models.Movie.id == db_swipe.movie_id).first()

    return {
        "id": db_swipe.id,
        "user_id": db_swipe.user_id,
        "movie_id": db_swipe.movie_id,
        "is_liked": db_swipe.is_liked,
        "created_at": db_swipe.created_at,
        "is_match": is_match,
        "movie": movie,
    }


async def populate_discover_movies(db: Session, page: int = 1) -> int:
    """Fetch movies from multiple TMDB sources concurrently and add new ones to DB."""
    genre_map, top_rated, now_playing, popular, trending = await asyncio.gather(
        tmdb.fetch_genres(),
        tmdb.fetch_top_rated_movies(page=page),
        tmdb.fetch_now_playing_movies(page=page),
        tmdb.fetch_popular_movies(page=page),
        tmdb.fetch_trending_movies(page=page),
    )

    all_results = top_rated + now_playing + popular + trending
    if not all_results:
        return 0

    # Дедупликация внутри пачки по TMDB ID (или названию)
    unique_items: list[dict] = []
    seen_tmdb_ids: set[int] = set()
    seen_titles: set[tuple[str, Optional[int]]] = set()

    for item in all_results:
        title = (item.get("title") or "").strip()
        if not title:
            continue

        release_date = item.get("release_date") or ""
        year: Optional[int] = None
        if len(release_date) >= 4 and release_date[:4].isdigit():
            year = int(release_date[:4])

        tmdb_id = item.get("id")
        if tmdb_id is not None:
            if tmdb_id in seen_tmdb_ids:
                continue
            seen_tmdb_ids.add(tmdb_id)
        else:
            key = (title, year)
            if key in seen_titles:
                continue
            seen_titles.add(key)

        item["_parsed_title"] = title
        item["_parsed_year"] = year
        unique_items.append(item)

    if not unique_items:
        return 0

    # Загружаем уже существующие фильмы одним запросом вместо N+1
    existing_by_tmdb_id: dict[int, models.Movie] = {}
    if seen_tmdb_ids:
        for m in db.query(models.Movie).filter(models.Movie.tmdb_id.in_(seen_tmdb_ids)).all():
            if m.tmdb_id is not None:
                existing_by_tmdb_id[m.tmdb_id] = m

    titles_to_check = {item["_parsed_title"] for item in unique_items}
    existing_by_title_year: dict[tuple[str, Optional[int]], models.Movie] = {}
    for m in db.query(models.Movie).filter(models.Movie.title.in_(titles_to_check)).all():
        existing_by_title_year[(m.title, m.year)] = m

    added_count = 0
    dirty = False

    for item in unique_items:
        title = item["_parsed_title"]
        year = item["_parsed_year"]
        tmdb_id = item.get("id")
        genre_ids = item.get("genre_ids", [])
        genre_names = [genre_map[gid].lower() for gid in genre_ids if gid in genre_map]

        exists = (
            existing_by_tmdb_id.get(tmdb_id)
            if tmdb_id is not None
            else None
        ) or existing_by_title_year.get((title, year))

        if not exists:
            poster_path = item.get("poster_path")
            poster_url = f"{tmdb.TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None

            movie = models.Movie(
                tmdb_id=tmdb_id,
                title=title,
                year=year,
                genres=genre_names,
                poster_url=poster_url,
                rating=item.get("vote_average"),
                description=item.get("overview"),
            )
            db.add(movie)
            added_count += 1
            dirty = True
        else:
            if exists.tmdb_id is None and tmdb_id is not None:
                exists.tmdb_id = tmdb_id
                dirty = True
            if not exists.genres and genre_names:
                exists.genres = genre_names
                dirty = True

    if dirty:
        db.commit()
    return added_count


async def get_next_movie(
    db: Session,
    user_id: int,
    min_year: Optional[int] = None,
    genre: Optional[Union[str, List[str]]] = None,
) -> Optional[models.Movie]:
    global _background_discover_running

    query = db.query(models.Movie)

    swiped_subquery = db.query(models.Swipe.movie_id).filter(models.Swipe.user_id == user_id)
    query = query.filter(~models.Movie.id.in_(swiped_subquery))

    if min_year:
        query = query.filter(models.Movie.year >= min_year)

    if genre:
        genres_list = [genre] if isinstance(genre, str) else list(genre)
        genres_list = [g.lower() for g in genres_list if g]
        if genres_list:
            genre_filters = [models.Movie.genres.any(g) for g in genres_list]
            query = query.filter(or_(*genre_filters))

    movie = query.order_by(models.Movie.id).first()

    # Предзагрузка в фоне без параллельного шторма запросов к TMDB
    count = query.count()
    if count < 20 and not _background_discover_running:
        from .database import SessionLocal
        asyncio.create_task(populate_discover_batch(pages=5, db_session=SessionLocal))

    if movie and not movie.poster_url:
        poster_url = await tmdb.fetch_poster_url(movie.title, movie.year)
        if poster_url:
            movie.poster_url = poster_url
            db.commit()
            db.refresh(movie)

    return movie


async def populate_discover_batch(pages: int = 5, start_page: int = 1, db_session=None) -> int:
    """Загрузить несколько страниц фильмов из TMDB в фоне."""
    global _background_discover_running
    if _background_discover_running:
        return 0

    _background_discover_running = True
    db = db_session()
    total_added = 0
    try:
        for page in range(start_page, start_page + pages):
            total_added += await populate_discover_movies(db, page=page)
        return total_added
    except Exception as e:
        print(f"[CRUD] Error in background discover batch: {e}")
        db.rollback()
        return total_added
    finally:
        db.close()
        _background_discover_running = False


def clear_user_swipes(db: Session, user_id: int) -> None:
    db.query(models.Swipe).filter(models.Swipe.user_id == user_id).delete()
    db.commit()


def get_active_users(db: Session) -> List[models.User]:
    return db.query(models.User).order_by(models.User.id).all()


def delete_user(db: Session, user_id: int) -> None:
    """Удалить пользователя и все его свайпы."""
    db.query(models.Swipe).filter(models.Swipe.user_id == user_id).delete()
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
