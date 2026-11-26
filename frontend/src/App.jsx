import React, { useState, useEffect, useCallback } from 'react';
import SwipeScreen from './components/SwipeScreen';
import LoginScreen from './components/LoginScreen';

function App() {
  const [user, setUser] = useState(null);

  const handleLogout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('movie_matcher_user');
    localStorage.removeItem('token');
  }, []);

  useEffect(() => {
    const savedUser = localStorage.getItem('movie_matcher_user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        handleLogout();
      }
    }

    window.addEventListener('auth:unauthorized', handleLogout);
    return () => window.removeEventListener('auth:unauthorized', handleLogout);
  }, [handleLogout]);

  const handleLogin = (newUser) => {
    setUser(newUser);
    localStorage.setItem('movie_matcher_user', JSON.stringify(newUser));
  };

  if (!user) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="relative">
      <SwipeScreen />
      <button
        onClick={handleLogout}
        className="fixed top-4 right-4 z-10 text-gray-500 hover:text-white text-xs underline bg-gray-900/50 p-1 rounded"
      >
        Сменить пользователя ({user.username})
      </button>
    </div>
  );
}

export default App;
