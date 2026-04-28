import React, { useState } from 'react';
import Header from './components/Header';
import GenerationForm from './components/GenerationForm';
import SlidesPreview from './components/SlidesPreview';
import Loader from './components/Loader';
import { generatePresentation } from './services/api';
import styles from './App.module.scss';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [slides, setSlides] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async (request) => {
    setLoading(true);
    setError(null);

    try {
      const response = await generatePresentation(request);
      setSlides(response.slides);
      setSessionId(response.session_id);
    } catch (err) {
      console.error('Generation error:', err);
      setError(err.response?.data?.detail || 'Ошибка при генерации презентации');
      setTimeout(() => setError(null), 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleSlidesUpdate = (updatedSlides) => {
    setSlides(updatedSlides);
  };

  return (
    <div className={styles.app}>
      <Header />
      <main className={styles.main}>
        {!loading && slides.length === 0 && (
          <GenerationForm onSubmit={handleGenerate} loading={loading} />
        )}

        {error && (
          <div className={styles.errorToast}>
            {error}
          </div>
        )}

        {loading && <Loader message="ИИ анализирует запрос и создает презентацию..." />}

        {!loading && slides.length > 0 && sessionId && (
          <SlidesPreview
            slides={slides}
            sessionId={sessionId}
            onSlidesUpdate={handleSlidesUpdate}
          />
        )}
      </main>
    </div>
  );
};

export default App;