from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import os

from . import models, schemas, crud, auth
from .database import SessionLocal, engine, get_db

app = FastAPI(title="Movie Matcher API")

# CORS - только разрешённые домены
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя."""
    return crud.get_or_create_user(db, username=user.username)


@app.post("/login", response_model=auth.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Получить JWT токен для пользователя."""
    db_user = crud.get_or_create_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": db_user["username"], "user_id": db_user["id"]},
        expires_delta=access_token_expires
    )
    return auth.Token(access_token=access_token, user_id=db_user["id"])


async def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
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


from datetime import datetime

@app.get("/movies/next", response_model=schemas.MovieResponse)
async def get_next_movie(
    exclude_watched: bool = False,
    max_age: Optional[int] = None,
    genre: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    min_year = None
    if max_age is not None:
        current_year = datetime.now().year
        min_year = current_year - max_age

    movie = await crud.get_next_movie(db, user_id=current_user.id, exclude_watched=exclude_watched, min_year=min_year, genre=genre)
    if not movie:
        raise HTTPException(status_code=404, detail="No movies left to swipe!")
    return movie


@app.post("/movies/discover")
async def discover_movies(page: int = None, db: Session = Depends(get_db)):
    """Manually trigger discovery of more movies from TMDB."""
    import random
    if page is None:
        page = random.randint(1, 5)
    added = await crud.populate_discover_movies(db, page=page)
    return {"message": f"Added {added} new movies", "page": page}


@app.get("/users/active", response_model=List[schemas.UserResponse])
def get_active_users(db: Session = Depends(get_db)):
    return crud.get_active_users(db)


@app.delete("/users/me/swipes")
def clear_my_swipes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Очистить свайпы текущего пользователя."""
    crud.clear_user_swipes(db, current_user.id)
    return {"message": "Swipe history cleared"}


@app.post("/swipe", response_model=schemas.SwipeResponse)
def create_swipe(swipe: schemas.SwipeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Создать свайп от имени текущего пользователя."""
    # Принудительно устанавливаем user_id из токена
    swipe_data = schemas.SwipeCreate(user_id=current_user.id, movie_id=swipe.movie_id, is_liked=swipe.is_liked)
    return crud.create_swipe(db, swipe=swipe_data)
