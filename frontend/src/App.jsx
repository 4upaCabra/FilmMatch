import React, { useState, useEffect } from 'react';
import SwipeScreen from './components/SwipeScreen';
import LoginScreen from './components/LoginScreen';

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('movie_matcher_user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (newUser) => {
    setUser(newUser);
    localStorage.setItem('movie_matcher_user', JSON.stringify(newUser));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('movie_matcher_user');
    localStorage.removeItem('token');
  };

  if (!user) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <div className="relative">
      <SwipeScreen user={user} />
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
