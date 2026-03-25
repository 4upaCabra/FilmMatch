import React, { useState, useEffect } from 'react';
import UploadCsvScreen from './components/UploadCsvScreen';
import SwipeScreen from './components/SwipeScreen';
import LoginScreen from './components/LoginScreen';

function App() {
  const [user, setUser] = useState(null);
  const [hasUploaded, setHasUploaded] = useState(false);

  // Persistence for testing between tabs
  useEffect(() => {
    const savedUser = localStorage.getItem('movie_matcher_user');
    if (savedUser) {
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
    setHasUploaded(false);
  };

  if (!user) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (!hasUploaded) {
    return (
      <div className="relative">
        <UploadCsvScreen 
          userId={user.id} 
          onUploadSuccess={() => {
            setHasUploaded(true);
            // Refresh user to get has_history: true
            loginUser(user.username).then(newUser => {
               setUser(newUser);
               localStorage.setItem('movie_matcher_user', JSON.stringify(newUser));
            });
          }} 
        />
        <button 
          onClick={handleLogout}
          className="absolute top-4 right-4 text-gray-500 hover:text-white text-xs underline"
        >
          Сменить пользователя ({user.username})
        </button>
      </div>
    );
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
