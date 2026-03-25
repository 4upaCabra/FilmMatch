import React, { useState } from 'react';
import { uploadKpJson, clearUserSwipes } from '../api/client';

export default function UploadScreen({ userId, onUploadSuccess }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await clearUserSwipes(userId);
      onUploadSuccess();
    } catch (err) {
      setError('Не удалось очистить историю. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Выберите хотя бы один JSON-файл из экспорта Кинопоиска.');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const resp = await uploadKpJson(userId, files);
      setMessage(`Успех! Добавлено ${resp.movies_added} фильмов и ${resp.history_added} записей истории.`);
      setTimeout(() => {
        onUploadSuccess();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при загрузке.');
    } finally {
      setLoading(false);
    }
  };

  const fileLabel = files.length === 0
    ? 'Выберите JSON-файлы из экспорта'
    : files.map(f => f.name).join(', ');

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 px-4">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl max-w-md w-full border border-gray-700">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600 mb-2 text-center">
          Выбор фильма
        </h2>

        <div className="flex justify-center mb-6">
          <button
            onClick={handleStart}
            disabled={loading}
            className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-xl transition-all uppercase tracking-wider disabled:opacity-50"
          >
            {loading ? 'Загрузка...' : 'Начать'}
          </button>
        </div>

        <p className="text-gray-400 text-sm mb-2 text-center">
          Загрузите JSON-файлы из экспорта Кинопоиска.
        </p>
        <p className="text-gray-500 text-xs mb-6 text-center">
          Выберите <span className="text-purple-400">vote_*.json</span> (обязательно),
          а также <span className="text-purple-400">folder_*.json</span> и{' '}
          <span className="text-purple-400">view_log_*.json</span> (опционально)
        </p>

        <div className="mb-6">
          <label className="flex flex-col items-center px-4 py-6 bg-gray-900 text-gray-400 rounded-xl border-2 border-dashed border-gray-700 cursor-pointer hover:border-purple-500 hover:text-purple-400 transition-colors">
            <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            <span className="text-sm text-center break-all">{fileLabel}</span>
            <input
              type="file"
              accept=".json"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
          </label>
        </div>

        {error && <div className="text-red-400 text-sm text-center mb-4">{error}</div>}
        {message && <div className="text-green-400 text-sm text-center mb-4 font-medium">{message}</div>}

        <button
          onClick={handleUpload}
          disabled={loading || files.length === 0}
          className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider"
        >
          {loading ? 'Обработка...' : 'Загрузить из Кинопоиска'}
        </button>

      </div>
    </div>
  );
}
