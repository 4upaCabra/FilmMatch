import httpx
import os
from typing import Optional

TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


async def _fetch_from_tmdb(endpoint: str, params: dict) -> list:
    headers = {}
    if TMDB_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {TMDB_BEARER_TOKEN}"
    else:
        params["api_key"] = TMDB_API_KEY

    url = f"{TMDB_BASE_URL}{endpoint}"
    proxy = "http://192.168.2.123:3128"

    try:
        async with httpx.AsyncClient(verify=False, proxies=proxy) as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching from TMDB endpoint {endpoint}: {repr(e)}")
        return {}


async def fetch_poster_url(title: str, year: Optional[int] = None) -> Optional[str]:
    params = {"query": title, "language": "ru-RU"}
    if year:
        params["primary_release_year"] = year

    data = await _fetch_from_tmdb("/search/movie", params)
    results = data.get("results", [])

    # Fallback: try without year if no results
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
    """Fetch top rated movies from TMDB."""
    params = {"language": "ru-RU", "page": page}
    data = await _fetch_from_tmdb("/movie/top_rated", params)
    return data.get("results", [])


async def fetch_now_playing_movies(page: int = 1) -> list:
    """Fetch currently playing/new movies from TMDB."""
    params = {"language": "ru-RU", "page": page}
    data = await _fetch_from_tmdb("/movie/now_playing", params)
    return data.get("results", [])


async def fetch_popular_movies(page: int = 1) -> list:
    """Fetch popular movies from TMDB."""
    params = {"language": "ru-RU", "page": page}
    data = await _fetch_from_tmdb("/movie/popular", params)
    return data.get("results", [])


async def fetch_upcoming_movies(page: int = 1) -> list:
    """Fetch upcoming movies from TMDB."""
    params = {"language": "ru-RU", "page": page}
    data = await _fetch_from_tmdb("/movie/upcoming", params)
    return data.get("results", [])


async def fetch_trending_movies(page: int = 1) -> list:
    """Fetch trending movies from TMDB (daily)."""
    params = {"language": "ru-RU"}
    data = await _fetch_from_tmdb("/trending/movie/day", params)
    return data.get("results", [])


async def fetch_genres() -> dict:
    """Fetch genre mapping from TMDB."""
    params = {"language": "ru-RU"}
    data = await _fetch_from_tmdb("/genre/movie/list", params)
    genres = data.get("genres", [])
    return {g["id"]: g["name"] for g in genres}
