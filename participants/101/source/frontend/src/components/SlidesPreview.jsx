import React, { useState } from 'react';
import { FaEdit, FaDownload, FaChevronLeft, FaChevronRight, FaImage, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import SlideEditor from './SlideEditor';
import { downloadPresentation } from '../services/api';
import styles from './SlidesPreview.module.scss';

const SlidesPreview = ({ slides, sessionId, onSlidesUpdate }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [editingSlide, setEditingSlide] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setDownloadError(null);
    setDownloadSuccess(false);

    try {
      if (!sessionId) {
        throw new Error('ID сессии не найден');
      }

      const blob = await downloadPresentation(sessionId);
      
      if (!blob || blob.size === 0) {
        throw new Error('Ошибка: получен пустой файл');
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presentation_${new Date().toISOString().split('T')[0]}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setDownloadSuccess(true);
      setTimeout(() => setDownloadSuccess(false), 3000);
    } catch (error) {
      console.error('Download failed:', error);
      
      let errorMsg = 'Ошибка при скачивании презентации';
      if (error.response?.status === 404) {
        errorMsg = 'Файл презентации не найден. Попробуйте перегенерировать.';
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setDownloadError(errorMsg);
      setTimeout(() => setDownloadError(null), 5000);
    } finally {
      setDownloading(false);
    }
  };

  const handleSaveSlide = (index, updatedSlide) => {
    const newSlides = [...slides];
    newSlides[index] = updatedSlide;
    onSlidesUpdate(newSlides);
  };

  const nextSlide = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  if (!slides || slides.length === 0) {
    return (
      <div className={styles.preview}>
        <div className={styles.error}>
          <FaExclamationTriangle />
          <p>Нет слайдов для отображения</p>
        </div>
      </div>
    );
  }

  const current = slides[currentSlide];

  return (
    <div className={styles.preview}>
      <div className={styles.header}>
        <h2>Предпросмотр презентации</h2>
        <div className={styles.actions}>
          <button onClick={() => setEditingSlide(currentSlide)} className={styles.editButton} title="Редактировать текущий слайд">
            <FaEdit /> Редактировать слайд
          </button>
          <button 
            onClick={handleDownload} 
            className={styles.downloadButton} 
            disabled={downloading}
            title={downloading ? 'Скачивание...' : 'Скачать презентацию в формате PPTX'}
          >
            <FaDownload /> {downloading ? 'Скачивание...' : 'Скачать PPTX'}
          </button>
        </div>
      </div>

      {downloadError && (
        <div className={styles.errorMessage}>
          <FaExclamationTriangle />
          <span>{downloadError}</span>
        </div>
      )}

      {downloadSuccess && (
        <div className={styles.successMessage}>
          <FaCheckCircle />
          <span>Презентация успешно скачана!</span>
        </div>
      )}

      <div className={styles.carousel}>
        <button onClick={prevSlide} className={styles.navButton} disabled={currentSlide === 0} aria-label="Предыдущий слайд">
          <FaChevronLeft />
        </button>

        <div className={styles.viewer}>
          <div className={styles.slide}>
            <div className={styles.slideNumber}>
              Слайд {currentSlide + 1} / {slides.length}
            </div>
            <div className={styles.slideTitle}>{current?.title || 'Без названия'}</div>
            <div className={styles.slideContent}>
              {current?.content?.split('\n').map((line, idx) => (
                line.trim() && (
                  <div key={idx} className={styles.bullet}>
                    • {line.trim()}
                  </div>
                )
              ))}
            </div>
            {current?.image_url && (
              <div className={styles.slideImage}>
                <img src={current.image_url} alt={current.title} loading="lazy" />
              </div>
            )}
            {!current?.image_url && current?.image_prompt && (
              <div className={styles.imagePlaceholder}>
                <FaImage />
                <span>Изображение будет сгенерировано</span>
              </div>
            )}
          </div>
        </div>

        <button onClick={nextSlide} className={styles.navButton} disabled={currentSlide === slides.length - 1} aria-label="Следующий слайд">
          <FaChevronRight />
        </button>
      </div>

      <div className={styles.thumbnails}>
        {slides.map((slide, idx) => (
          <div
            key={idx}
            className={`${styles.thumbnail} ${idx === currentSlide ? styles.active : ''}`}
            onClick={() => setCurrentSlide(idx)}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                setCurrentSlide(idx);
              }
            }}
          >
            <div className={styles.thumbnailNumber}>{idx + 1}</div>
            <div className={styles.thumbnailTitle}>{slide.title.substring(0, 30)}</div>
          </div>
        ))}
      </div>

      {editingSlide !== null && (
        <SlideEditor
          slide={slides[editingSlide]}
          index={editingSlide}
          onSave={handleSaveSlide}
          onClose={() => setEditingSlide(null)}
        />
      )}
    </div>
  );
};

export default SlidesPreview;