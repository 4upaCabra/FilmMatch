from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas, crud
from .database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Matcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users", response_model=schemas.UserResponse)
def get_or_create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.get_or_create_user(db, username=user.username)


from datetime import datetime

@app.get("/movies/next", response_model=schemas.MovieResponse)
async def get_next_movie(
    user_id: int,
    exclude_watched: bool = False,
    max_age: Optional[int] = None,
    genre: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db)
):
    min_year = None
    if max_age is not None:
        current_year = datetime.now().year
        min_year = current_year - max_age

    movie = await crud.get_next_movie(db, user_id=user_id, exclude_watched=exclude_watched, min_year=min_year, genre=genre)
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


@app.delete("/users/{user_id}/swipes")
def clear_user_swipes(user_id: int, db: Session = Depends(get_db)):
    crud.clear_user_swipes(db, user_id)
    return {"message": "Swipe history cleared"}


@app.post("/swipe", response_model=schemas.SwipeResponse)
def create_swipe(swipe: schemas.SwipeCreate, db: Session = Depends(get_db)):
    return crud.create_swipe(db, swipe=swipe)
