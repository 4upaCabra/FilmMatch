import axios from 'axios';

const api = axios.create({
  baseURL: `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8001`,
});

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const registerUser = async (username) => {
  const response = await api.post('/register', { username });
  return response.data;
};

export const loginUser = async (username) => {
  const response = await api.post('/login', { username });
  return response.data;
};

export const getNextMovie = async (excludeWatched, maxAge, genre) => {
  const response = await api.get('/movies/next', {
    params: {
      exclude_watched: excludeWatched,
      max_age: maxAge,
      genre: genre
    },
    paramsSerializer: {
      indexes: null
    }
  });
  return response.data;
};

export const swipeMovie = async (movieId, isLiked) => {
  const response = await api.post('/swipe', {
    movie_id: movieId,
    is_liked: isLiked
  });
  return response.data;
};

export const clearUserSwipes = async () => {
  const response = await api.delete('/users/me/swipes');
  return response.data;
};

export const discoverMovies = async (page = null) => {
  const params = {};
  if (page !== null) {
    params.page = page;
  }
  const response = await api.post('/movies/discover', null, { params });
  return response.data;
};

export const getActiveUsers = async () => {
  const response = await api.get('/users/active');
  return response.data;
};

export const deleteUser = async (userId) => {
  const response = await api.delete(`/users/${userId}`);
  return response.data;
};

export default api;
