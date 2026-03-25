from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    has_history: bool = False

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str

class MovieBase(BaseModel):
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

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True
