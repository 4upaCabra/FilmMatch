from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)

    swipes = relationship("Swipe", back_populates="user", cascade="all, delete-orphan")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    genres = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    rating = Column(Float, nullable=True)
    poster_url = Column(String, nullable=True)
    description = Column(String, nullable=True)

    swipes = relationship("Swipe", back_populates="movie", cascade="all, delete-orphan")


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="_user_movie_swipe_uc"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    is_liked = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    user = relationship("User", back_populates="swipes")
    movie = relationship("Movie", back_populates="swipes")
