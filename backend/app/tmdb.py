import os
from typing import Optional
import httpx

TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

_genre_cache: Optional[dict[int, str]] = None


async def _fetch_from_tmdb(endpoint: str, params: dict) -> dict:
    headers = {}
    req_params = dict(params)
    if TMDB_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_BEARER_TOKEN}"
    elif TMDB_API_KEY:
        req_params["api_key"] = TMDB_API_KEY

    url = f"{TMDB_BASE_URL}{endpoint}"
    proxy = os.getenv("TMDB_PROXY_URL") or None

    try:
        async with httpx.AsyncClient(proxy=proxy, timeout=10.0) as client:
            response = await client.get(url, params=req_params, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching from TMDB endpoint {endpoint}: {repr(e)}")
        return {}


async def fetch_poster_url(title: str, year: Optional[int] = None) -> Optional[str]:
    params: dict = {"query": title, "language": "ru-RU"}
    if year:
        params["primary_release_year"] = year

    data = await _fetch_from_tmdb("/search/movie", params)
    results = data.get("results", [])

    if not results and year:
        params.pop("primary_release_year", None)
        data = await _fetch_from_tmdb("/search/movie", params)
        results = data.get("results", [])

    if results:
        poster_path = results[0].get("poster_path")
        if poster_path:
            return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    return None


async def fetch_top_rated_movies(page: int = 1) -> list:
    data = await _fetch_from_tmdb("/movie/top_rated", {"language": "ru-RU", "page": page})
    return data.get("results", [])


async def fetch_now_playing_movies(page: int = 1) -> list:
    data = await _fetch_from_tmdb("/movie/now_playing", {"language": "ru-RU", "page": page})
    return data.get("results", [])


async def fetch_popular_movies(page: int = 1) -> list:
    data = await _fetch_from_tmdb("/movie/popular", {"language": "ru-RU", "page": page})
    return data.get("results", [])


async def fetch_trending_movies(page: int = 1) -> list:
    data = await _fetch_from_tmdb("/trending/movie/day", {"language": "ru-RU", "page": page})
    return data.get("results", [])


async def fetch_genres() -> dict[int, str]:
    global _genre_cache
    if _genre_cache:
        return _genre_cache

    data = await _fetch_from_tmdb("/genre/movie/list", {"language": "ru-RU"})
    genres = data.get("genres", [])
    if genres:
        _genre_cache = {g["id"]: g["name"] for g in genres}
        return _genre_cache
    return {}
