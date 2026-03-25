import React from 'react';

// Обрезает описание до последнего полного предложения (максимум ~6 строк)
function truncateDescription(text, maxLines = 6) {
  if (!text) return '';

  // Ограничиваем по символам с учётом maxLines (~40 символов на строку)
  const maxChars = maxLines * 40;

  if (text.length <= maxChars) {
    return text;
  }

  // Обрезаем до maxChars и находим последнюю точку
  const truncated = text.slice(0, maxChars);
  const lastDotIndex = truncated.lastIndexOf('.');

  if (lastDotIndex > 0) {
    return truncated.slice(0, lastDotIndex + 1);
  }

  // Если точек нет, просто обрезаем и добавляем многоточие
  return truncated + '...';
}

export default function MovieCard({ movie, onSwipe }) {
  if (!movie) return null;

  const description = truncateDescription(movie.description);

  return (
    <div className="bg-gray-800 rounded-2xl shadow-2xl overflow-hidden max-w-sm w-full relative">
      <div className="h-[400px] bg-gray-800 flex items-center justify-center">
        {movie.poster_url ? (
          <img src={movie.poster_url} alt={movie.title} className="w-full h-full object-contain" />
        ) : (
          <span className="text-gray-400 font-medium text-xl text-center px-4">Постер недоступен</span>
        )}
      </div>
      <div className="p-6">
        {(movie.rating || movie.genres?.length > 0) && (
          <div className="mt-4 flex flex-wrap gap-2">
            {movie.rating && (
              <span className="bg-yellow-500/20 text-yellow-300 px-3 py-1 rounded-full text-xs font-medium">
                ⭐ {movie.rating}
              </span>
            )}
            {movie.genres?.slice(0, 3).map(g => (
              <span key={g} className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-xs font-medium">
                {g}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between p-4 border-t border-gray-700 bg-gray-800/50 mt-4">
          <button
            onClick={() => onSwipe(false)}
            className="p-4 rounded-full bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all transform hover:scale-110 shadow-[0_0_15px_rgba(239,68,68,0.2)] hover:shadow-[0_0_25px_rgba(239,68,68,0.5)]"
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
          <div className="text-center">
            <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
              {movie.title}
            </h2>
            <p className="text-gray-400 text-sm">{movie.year ? movie.year : 'Год неизвестен'}</p>
          </div>
          <button
            onClick={() => onSwipe(true)}
            className="p-4 rounded-full bg-green-500/10 text-green-500 hover:bg-green-500 hover:text-white transition-all transform hover:scale-110 shadow-[0_0_15px_rgba(34,197,94,0.2)] hover:shadow-[0_0_25px_rgba(34,197,94,0.5)]"
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>
          </button>
        </div>

        {description && (
          <p className="text-gray-300 mt-4 text-sm">{description}</p>
        )}
      </div>
    </div>
  );
}
