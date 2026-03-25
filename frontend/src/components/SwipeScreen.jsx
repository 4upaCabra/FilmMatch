import React, { useState, useEffect, useCallback } from 'react';
import { getNextMovie, swipeMovie, discoverMovies } from '../api/client';
import MovieCard from './MovieCard';

const POPULAR_GENRES = [
  "Боевик", "Приключения", "Мультфильм", "Комедия", "Криминал",
  "Драма", "Фэнтези", "Ужасы", "Мелодрама", "Фантастика", "Триллер"
];

export default function SwipeScreen({ user }) {
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [excludeWatched, setExcludeWatched] = useState(false);
  const [maxAge, setMaxAge] = useState(1);
  const [genre, setGenre] = useState([]);
  const [error, setError] = useState('');
  const [matchMovie, setMatchMovie] = useState(null);

  // Pending filters (not yet applied)
  const [pendingExcludeWatched, setPendingExcludeWatched] = useState(false);
  const [pendingMaxAge, setPendingMaxAge] = useState(1);
  const [pendingGenre, setPendingGenre] = useState([]);
  const [hasPendingChanges, setHasPendingChanges] = useState(false);

  const fetchMovie = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const nextMovie = await getNextMovie(excludeWatched, maxAge, genre);
      setMovie(nextMovie);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Попробуйте расширить фильтры.');
        setMovie(null);
      } else {
        setError('Не удалось загрузить следующий фильм.');
        setMovie(null);
      }
    } finally {
      setLoading(false);
    }
  }, [excludeWatched, maxAge, genre]);

  useEffect(() => {
    fetchMovie();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const applyFilters = useCallback(() => {
    setExcludeWatched(pendingExcludeWatched);
    setMaxAge(pendingMaxAge);
    setGenre(pendingGenre);
    setHasPendingChanges(false);
    fetchMovie();
  }, [pendingExcludeWatched, pendingMaxAge, pendingGenre, fetchMovie]);

  useEffect(() => {
    const hasChanges = (
      pendingExcludeWatched !== excludeWatched ||
      pendingMaxAge !== maxAge ||
      JSON.stringify(pendingGenre) !== JSON.stringify(genre)
    );
    setHasPendingChanges(hasChanges);
  }, [pendingExcludeWatched, pendingMaxAge, pendingGenre, excludeWatched, maxAge, genre]);

  const handleSwipe = async (isLiked) => {
    if (!movie) return;

    // Optimistic UI update
    const currentMovieId = movie.id;
    setMovie(null);

    try {
      const res = await swipeMovie(currentMovieId, isLiked);
      console.log('Swipe response:', res);

      if (res.is_match) {
        console.log('MATCH! Movie:', res.movie);
        setMatchMovie(res.movie);
      } else {
        fetchMovie();
      }
    } catch (err) {
      console.error('Failed to save swipe', err);
      setError('Ошибка подключения при записи свайпа.');
      fetchMovie();
    }
  };

  const adjustMaxAge = (delta) => {
    setPendingMaxAge(prev => {
      const next = prev + delta;
      return Math.max(1, Math.min(40, next));
    });
  };

  const toggleGenre = (g) => {
    if (g === '') {
      setPendingGenre([]);
    } else {
      setPendingGenre(prev =>
        prev.includes(g)
          ? prev.filter(item => item !== g)
          : [...prev, g]
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center pt-8 px-4 pb-20 relative overflow-x-hidden">

      {/* Match Overlay */}
      {matchMovie && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md p-6">
          <div className="bg-gray-800 border border-purple-500/50 rounded-3xl p-8 max-w-sm w-full shadow-[0_0_50px_rgba(168,85,247,0.4)] text-center animate-in zoom-in duration-300">
            <div className="text-5xl mb-4 animate-bounce">🔥</div>
            <h2 className="text-4xl font-black text-white mb-2 tracking-tighter uppercase italic">
              Это матч!
            </h2>
            <p className="text-purple-400 font-medium mb-6">Вы оба выбрали этот фильм</p>

            <div className="aspect-[2/3] w-48 mx-auto mb-6 rounded-2xl overflow-hidden shadow-2xl border-2 border-purple-500">
              <img
                src={matchMovie.poster_url || 'https://via.placeholder.com/500x750?text=No+Poster'}
                alt={matchMovie.title}
                className="w-full h-full object-cover"
              />
            </div>

            <h3 className="text-xl font-bold text-white mb-8">{matchMovie.title}</h3>

            <button
              onClick={() => {
                setMatchMovie(null);
                fetchMovie();
              }}
              className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-black rounded-2xl shadow-lg hover:shadow-purple-500/50 transition-all transform hover:scale-105 active:scale-95"
            >
              ПРОДОЛЖИТЬ
            </button>
          </div>
        </div>
      )}

      {/* Main card area - Top section */}
      <div className="flex-1 flex flex-col items-center justify-center w-full max-w-sm mb-6">
        {loading && !movie && (
          <div className="flex items-center space-x-2 animate-pulse text-purple-400">
            <div className="w-4 h-4 rounded-full bg-purple-400"></div>
            <div className="w-4 h-4 rounded-full bg-purple-400"></div>
            <div className="w-4 h-4 rounded-full bg-purple-400"></div>
          </div>
        )}

        {error && !loading && !movie && (
          <div className="text-gray-400 text-center bg-gray-800 p-8 rounded-2xl w-full border border-gray-700 shadow-xl">
            <div className="text-4xl mb-4">🎬</div>
            <p>{error}</p>
            <div className="flex flex-col gap-3 mt-6">
              <button
                onClick={async () => {
                  setError('');
                  setLoading(true);
                  try {
                    // Загружаем 10 страниц вручную
                    for (let page = 1; page <= 10; page++) {
                      await discoverMovies(page);
                    }
                    await fetchMovie();
                  } catch (e) {
                    setError('Попробуйте расширить фильтры.');
                  } finally {
                    setLoading(false);
                  }
                }}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-xl shadow-lg hover:shadow-purple-500/50 transition-all"
              >
                Загрузить ещё фильмов
              </button>
              <button
                onClick={() => {
                  setPendingExcludeWatched(false);
                  setPendingGenre([]);
                  setPendingMaxAge(5);
                  applyFilters();
                }}
                className="text-purple-400 hover:text-purple-300 font-medium underline"
              >
                Сбросить фильтры
              </button>
            </div>
          </div>
        )}

        {!loading && movie && (
          <MovieCard movie={movie} onSwipe={handleSwipe} />
        )}
      </div>

      {/* Bottom controls - Age, Genres, Apply Button */}
      <div className="w-full max-w-sm flex flex-col items-center px-2 space-y-3 mt-4">
        {/* Age Filter */}
        <div className="w-full bg-gray-800 p-4 rounded-xl border border-gray-700 shadow-md">
          <div className="flex items-center justify-between mb-3 text-gray-300">
            <span className="text-sm font-medium">свежесть <span className="text-purple-400 font-bold">{pendingMaxAge}</span> лет</span>
            <div className="flex items-center bg-gray-900 rounded-lg p-1 border border-gray-700">
              <button
                onClick={() => adjustMaxAge(-1)}
                className="p-1 hover:text-purple-400 transition-colors"
                title="Уменьшить"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path></svg>
              </button>
              <div className="w-8 text-center text-xs font-bold text-gray-400">{pendingMaxAge}</div>
              <button
                onClick={() => adjustMaxAge(1)}
                className="p-1 hover:text-purple-400 transition-colors"
                title="Увеличить"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
              </button>
            </div>
          </div>
          <input
            type="range"
            min="1"
            max="40"
            value={pendingMaxAge}
            onChange={(e) => setPendingMaxAge(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>

        {/* Genre Filter - Multi-line and multi-select */}
        <div className="w-full">
          <div className="flex flex-wrap gap-2 justify-center">
            <button
              onClick={() => toggleGenre('')}
              className={`px-3 py-1.5 rounded-full text-[11px] font-bold border transition-all ${pendingGenre.length === 0
                ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-500/30'
                : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
                }`}
            >
              Все жанры
            </button>
            {POPULAR_GENRES.map(g => (
              <button
                key={g}
                onClick={() => toggleGenre(g)}
                className={`px-3 py-1.5 rounded-full text-[11px] font-bold border transition-all ${pendingGenre.includes(g)
                  ? 'bg-purple-600 border-purple-500 text-white shadow-lg shadow-purple-500/30'
                  : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
                  }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        {/* Apply Filters Button */}
        <button
          onClick={applyFilters}
          disabled={!hasPendingChanges}
          className={`w-full py-3 rounded-xl font-bold transition-all ${hasPendingChanges
            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg hover:shadow-purple-500/50 hover:scale-105'
            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
        >
          ПРИМЕНИТЬ ФИЛЬТРЫ
        </button>

        {/* Watched Toggle - Only if user has history */}
        {user.has_history && (
          <label className="inline-flex items-center cursor-pointer w-full justify-between bg-gray-800 p-3 rounded-xl border border-gray-700 shadow-md">
            <span className="mr-3 text-sm font-medium text-gray-300">Скрыть просмотренные</span>
            <div className="relative">
              <input
                type="checkbox"
                checked={pendingExcludeWatched}
                onChange={() => setPendingExcludeWatched(!pendingExcludeWatched)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </div>
          </label>
        )}
      </div>

    </div>
  );
}
