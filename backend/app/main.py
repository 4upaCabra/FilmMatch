from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import html
import re

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


def decode_html(text: str) -> str:
    """Decode HTML entities like &ndash; &amp; &#48; etc."""
    if not text:
        return text
    return html.unescape(text)


def upsert_movie_and_history(db, user_id: int, title: str, user_rating=None):
    """Find or create a movie, then add it to watch history if not already there."""
    movie = db.query(models.Movie).filter(models.Movie.title == title).first()
    movie_added = False
    if not movie:
        movie = models.Movie(title=title)
        db.add(movie)
        db.flush()
        movie_added = True

    history = db.query(models.WatchHistory).filter(
        models.WatchHistory.user_id == user_id,
        models.WatchHistory.movie_id == movie.id
    ).first()
    history_added = False
    if not history:
        history = models.WatchHistory(user_id=user_id, movie_id=movie.id, user_rating=user_rating)
        db.add(history)
        history_added = True
    elif user_rating is not None and history.user_rating is None:
        # Update rating if we now have one
        history.user_rating = user_rating

    return movie_added, history_added


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


@app.post("/upload-kp-json")
async def upload_kp_json(
    user_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Import Kinopoisk export JSON files.
    Accepted files (matched by filename pattern):
      - vote_*.json    — watch history with ratings (most important)
      - folder_*.json  — bookmarks ("Любимые фильмы" → add to history)
      - view_log_*.json — session view log
    """
    total_movies_added = 0
    total_history_added = 0

    for upload in files:
        filename = upload.filename or ""
        contents = await upload.read()
        try:
            records = json.loads(contents)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse {filename}: {e}")

        if not isinstance(records, list):
            raise HTTPException(status_code=400, detail=f"{filename}: expected a JSON array")

        # --- vote_*.json ---
        # Each item: {make_date, title, type ("просмотр"|"оценка"), vote}
        if re.match(r"vote_\d+\.json", filename):
            for item in records:
                title = decode_html(item.get("title", "").strip())
                if not title:
                    continue
                vote_str = item.get("vote", "0")
                try:
                    vote = int(vote_str)
                except (ValueError, TypeError):
                    vote = 0
                user_rating = vote if vote and vote > 0 else None
                m, h = upsert_movie_and_history(db, user_id, title, user_rating)
                if m:
                    total_movies_added += 1
                if h:
                    total_history_added += 1

        # --- folder_*.json ---
        # Each item: {folder_name, make_date, title}
        # Only "Любимые фильмы" goes into history; "Буду смотреть" is skipped.
        elif re.match(r"folder_\d+\.json", filename):
            for item in records:
                folder = item.get("folder_name", "")
                if folder != "Любимые фильмы":
                    continue
                title = decode_html(item.get("title", "").strip())
                if not title:
                    continue
                m, h = upsert_movie_and_history(db, user_id, title, None)
                if m:
                    total_movies_added += 1
                if h:
                    total_history_added += 1

        # --- view_log_*.json ---
        # Each item: {make_date, title, type ("film"|"serial")}
        elif re.match(r"view_log_\d+\.json", filename):
            for item in records:
                title = decode_html(item.get("title", "").strip())
                if not title:
                    continue
                m, h = upsert_movie_and_history(db, user_id, title, None)
                if m:
                    total_movies_added += 1
                if h:
                    total_history_added += 1

        else:
            # Unknown file — skip silently
            continue

    db.commit()
    return {
        "message": "Upload successful",
        "movies_added": total_movies_added,
        "history_added": total_history_added
    }
