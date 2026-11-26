from datetime import datetime, timedelta
from typing import List, Optional
import os
import random
import time

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .database import get_db

app = FastAPI(title="FilmMatch API")

raw_origins = os.getenv("FRONTEND_URL", "http://localhost:3000,http://localhost:5173")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
allow_all_origins = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else allowed_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["GET", "POST", "DELETE", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

_discover_calls: list[float] = []


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создать или вернуть существующего пользователя."""
    return crud.get_or_create_user(db, username=user.username)


@app.post("/login", response_model=auth.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Получить JWT токен для пользователя."""
    db_user = crud.get_or_create_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id},
        expires_delta=access_token_expires,
    )
    return auth.Token(access_token=access_token, user_id=db_user.id)


async def get_current_user(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Получить текущего пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth.decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


@app.get("/movies/next", response_model=schemas.MovieResponse)
async def get_next_movie(
    max_age: Optional[int] = None,
    genre: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    min_year = None
    if max_age is not None:
        min_year = datetime.now().year - max_age

    movie = await crud.get_next_movie(
        db,
        user_id=current_user.id,
        min_year=min_year,
        genre=genre,
    )
    if not movie:
        raise HTTPException(status_code=404, detail="No movies left to swipe!")
    return movie


@app.post("/movies/discover")
async def discover_movies(
    request: Request,
    page: Optional[int] = Query(default=None, ge=1, le=500),
    pages: int = Query(default=1, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """Загрузить новые фильмы из TMDB (одну страницу или пачку страниц за один вызов)."""
    global _discover_calls
    now = time.time()
    _discover_calls = [t for t in _discover_calls if now - t < 60]
    if len(_discover_calls) >= 5:
        raise HTTPException(status_code=429, detail="Too many discover requests. Max 5 per minute.")
    _discover_calls.append(now)

    start_page = page if page is not None else random.randint(1, 20)
    added = 0
    for current_page in range(start_page, start_page + pages):
        added += await crud.populate_discover_movies(db, page=current_page)

    return {
        "message": f"Added {added} new movies",
        "start_page": start_page,
        "pages": pages,
        "added": added,
    }


@app.get("/users/active", response_model=List[schemas.UserResponse])
def get_active_users(db: Session = Depends(get_db)):
    return crud.get_active_users(db)


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удалить пользователя и все его данные (завершить сессию)."""
    crud.delete_user(db, user_id)
    return {"message": "User deleted"}


@app.delete("/users/me/swipes")
def clear_my_swipes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Очистить свайпы текущего пользователя."""
    crud.clear_user_swipes(db, current_user.id)
    return {"message": "Swipe history cleared"}


@app.post("/swipe", response_model=schemas.SwipeResponse)
def create_swipe(
    swipe: schemas.SwipeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Создать свайп от имени текущего пользователя."""
    swipe_data = {
        "user_id": current_user.id,
        "movie_id": swipe.movie_id,
        "is_liked": swipe.is_liked,
    }
    return crud.create_swipe(db, swipe_data=swipe_data)
