import axios from 'axios';

const api = axios.create({
  baseURL: `http://${typeof window !== 'undefined' ? window.location.hostname : '192.168.2.146'}:8001`,
});

export const loginUser = async (username) => {
  const response = await api.post('/users', { username });
  return response.data;
};

export const getNextMovie = async (userId, excludeWatched, maxAge, genre) => {
  const response = await api.get('/movies/next', {
    params: { 
      user_id: userId, 
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

export const swipeMovie = async (userId, movieId, isLiked) => {
  const response = await api.post('/swipe', {
    user_id: userId,
    movie_id: movieId,
    is_liked: isLiked
  });
  return response.data;
};

export const clearUserSwipes = async (userId) => {
  const response = await api.delete(`/users/${userId}/swipes`);
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

export default api;
