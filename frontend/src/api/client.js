import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Сбрасываем протухшую сессию при 401 (например, после пересоздания БД)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/login')) {
      localStorage.removeItem('token');
      localStorage.removeItem('movie_matcher_user');
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);

export const registerUser = async (username) => {
  const response = await api.post('/register', { username });
  return response.data;
};

export const loginUser = async (username) => {
  const response = await api.post('/login', { username });
  return response.data;
};

export const getNextMovie = async (maxAge, genre) => {
  const response = await api.get('/movies/next', {
    params: {
      max_age: maxAge,
      genre,
    },
    paramsSerializer: {
      indexes: null,
    },
  });
  return response.data;
};

export const swipeMovie = async (movieId, isLiked) => {
  const response = await api.post('/swipe', {
    movie_id: movieId,
    is_liked: isLiked,
  });
  return response.data;
};

export const clearUserSwipes = async () => {
  const response = await api.delete('/users/me/swipes');
  return response.data;
};

export const discoverMovies = async (options = {}) => {
  const params = {};
  if (typeof options === 'number') {
    params.page = options;
  } else {
    if (options.page != null) params.page = options.page;
    if (options.pages != null) params.pages = options.pages;
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
