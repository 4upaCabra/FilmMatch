from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)

    history = relationship("WatchHistory", back_populates="user")
    swipes = relationship("Swipe", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    kp_id = Column(Integer, unique=True, index=True, nullable=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    genres = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    rating = Column(Float, nullable=True)
    poster_url = Column(String, nullable=True)
    description = Column(String, nullable=True)

    history = relationship("WatchHistory", back_populates="movie")
    swipes = relationship("Swipe", back_populates="movie")


class WatchHistory(Base):
    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_rating = Column(Integer, nullable=True)
    watched_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='_user_movie_uc'),)

    user = relationship("User", back_populates="history")
    movie = relationship("Movie", back_populates="history")


class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    is_liked = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="swipes")
    movie = relationship("Movie", back_populates="swipes")
