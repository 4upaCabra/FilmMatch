from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=10)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=10)


class MovieBase(BaseModel):
    tmdb_id: Optional[int] = None
    title: str
    year: Optional[int] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieResponse(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SwipeCreate(BaseModel):
    movie_id: int
    is_liked: bool


class SwipeResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    is_liked: bool
    created_at: datetime
    is_match: bool = False
    movie: Optional[MovieResponse] = None

    model_config = ConfigDict(from_attributes=True)
