import React, { useState, useEffect } from 'react';
import { loginUser, getActiveUsers, clearUserSwipes } from '../api/client';

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeSessions, setActiveSessions] = useState([]);

  const fetchActiveSessions = async () => {
    try {
      const sessions = await getActiveUsers();
      setActiveSessions(sessions);
    } catch (err) {
      console.error('Failed to fetch active sessions', err);
    }
  };

  useEffect(() => {
    fetchActiveSessions();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setError('');
    try {
      const user = await loginUser(username.trim());
      onLogin(user);
    } catch (err) {
      setError('Не удалось войти. Попробуйте другое имя.');
    } finally {
      setLoading(false);
    }
  };

  const terminateSession = async (user) => {
    if (!window.confirm(`Завершить сеанс пользователя ${user.username} (очистить его свайпы)?`)) return;
    
    try {
      await clearUserSwipes(user.id);
      fetchActiveSessions();
    } catch (err) {
      console.error('Failed to terminate session', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center px-4 py-10">
      <div className="bg-gray-800 p-8 rounded-3xl shadow-2xl max-w-sm w-full border border-gray-700 text-center mb-8">
        <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-2">
          TinderFilm
        </h1>
        <p className="text-gray-400 mb-8 font-medium">Кто сегодня выбирает кино?</p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <input
            type="text"
            placeholder="Ваше имя"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-2xl py-4 px-6 text-white text-lg focus:outline-none focus:border-purple-500 transition-colors"
            required
          />
          
          {error && <p className="text-red-400 text-sm">{error}</p>}
          
          <button
            type="submit"
            disabled={loading || !username.trim()}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-2xl shadow-lg hover:shadow-purple-500/50 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? 'Вход...' : 'ВОЙТИ'}
          </button>
        </form>
      </div>

      {activeSessions.length > 0 && (
        <div className="max-w-sm w-full">
          <h3 className="text-gray-400 text-sm font-bold uppercase tracking-widest mb-4 px-2">
            Активные сеансы
          </h3>
          <div className="space-y-2">
            {activeSessions.map(u => (
              <div key={u.id} className="group flex items-center justify-between bg-gray-800/50 border border-gray-700 p-4 rounded-2xl hover:bg-gray-800 transition-all">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
                    {u.username[0].toUpperCase()}
                  </div>
                  <span className="text-gray-200 font-medium">{u.username}</span>
                </div>
                <button 
                  onClick={() => terminateSession(u)}
                  className="p-2 text-gray-500 hover:text-red-500 transition-colors transform group-hover:scale-110"
                  title="Завершить сеанс"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
