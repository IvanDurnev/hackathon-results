// App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Header from './components/Header';
import GenerationForm from './components/GenerationForm';
import SlidesPreview from './components/SlidesPreview';
import Loader from './components/Loader';
import { generatePresentation } from './services/api';
import styles from './App.module.scss';

const AppContent = () => {
  const [loading, setLoading] = useState(false);
  const [slides, setSlides] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [errorDetails, setErrorDetails] = useState(null);
  const navigate = useNavigate();

  const handleGenerate = async (request) => {
    setLoading(true);
    setError(null);
    setErrorDetails(null);

    try {
      // Валидация на клиенте
      if (!request.prompt || request.prompt.trim().length < 3) {
        throw new Error('Тема презентации должна быть минимум 3 символа');
      }

      if (request.numSlides < 1 || request.numSlides > 20) {
        throw new Error('Количество слайдов должно быть от 1 до 20');
      }

      const response = await generatePresentation(request);
      
      if (!response.slides) {
        throw new Error('Ошибка: Получен пустой ответ от сервера');
      }

      setSlides(response.slides);
      setSessionId(response.sessionId);

      // Переход на страницу редактора
      navigate('/editor', {
        state: { slides: response.slides, sessionId: response.sessionId }
      });
      setLoading(false);
    } catch (err) {
      console.error('Generation error:', err);
      
      // Обработка различных типов ошибок
      let errorMessage = 'Ошибка при генерации презентации';
      let details = null;

      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }

      if (err.response?.status === 500) {
        details = 'Ошибка сервера. Пожалуйста, проверьте параметры и попробуйте снова.';
      } else if (err.response?.status === 400) {
        details = 'Неверные параметры запроса.';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Истекло время ожидания. Попробуйте ещё раз.';
      } else if (err.message && err.message.includes('Network')) {
        errorMessage = 'Ошибка подключения к серверу. Проверьте соединение.';
      }

      setError(errorMessage);
      setErrorDetails(details);
      
      // Автоматическое скрытие ошибки через 7 секунд
      setTimeout(() => {
        setError(null);
        setErrorDetails(null);
      }, 7000);
      
      setLoading(false);
    }
  };

  const handleClearError = () => {
    setError(null);
    setErrorDetails(null);
  };

  return (
    <div className={styles.app}>
      <Header />
      <main className={styles.main}>
        {error && (
          <div className={styles.errorToast}>
            <div className={styles.errorContent}>
              <div className={styles.errorTitle}>{error}</div>
              {errorDetails && <div className={styles.errorDetail}>{errorDetails}</div>}
            </div>
            <button 
              className={styles.errorClose}
              onClick={handleClearError}
              aria-label="Закрыть"
            >
              ✕
            </button>
          </div>
        )}

        <Routes>
          <Route path="/" element={
            !loading ? (
              <GenerationForm onSubmit={handleGenerate} loading={loading} />
            ) : (
              <Loader message="ИИ анализирует запрос и создает презентацию..." />
            )
          } />
          <Route path="/editor" element={
            <SlidesPreview
              slides={slides !== null ? slides : []}
              sessionId={sessionId !== null ? sessionId : null}
              onSlidesUpdate={(updatedSlides) => setSlides(updatedSlides)}
            />
          } />
        </Routes>
      </main>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;