import React, { useState } from 'react';
import { FaEdit, FaDownload, FaChevronLeft, FaChevronRight, FaImage } from 'react-icons/fa';
import SlideEditor from './SlideEditor';
import { downloadPresentation } from '../services/api';
import styles from './SlidesPreview.module.scss';

const SlidesPreview = ({ slides, sessionId, onSlidesUpdate }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [editingSlide, setEditingSlide] = useState(null);
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const blob = await downloadPresentation(sessionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `presentation_${sessionId}.pptx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Ошибка при скачивании презентации');
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

  const current = slides[currentSlide];

  return (
    <div className={styles.preview}>
      <div className={styles.header}>
        <h2>Предпросмотр презентации</h2>
        <div className={styles.actions}>
          <button onClick={() => setEditingSlide(currentSlide)} className={styles.editButton}>
            <FaEdit /> Редактировать слайд
          </button>
          <button onClick={handleDownload} className={styles.downloadButton} disabled={downloading}>
            <FaDownload /> {downloading ? 'Скачивание...' : 'Скачать PPTX'}
          </button>
        </div>
      </div>

      <div className={styles.carousel}>
        <button onClick={prevSlide} className={styles.navButton} disabled={currentSlide === 0}>
          <FaChevronLeft />
        </button>

        <div className={styles.viewer}>
          <div className={styles.slide}>
            <div className={styles.slideNumber}>
              Слайд {currentSlide + 1} / {slides.length}
            </div>
            <div className={styles.slideTitle}>{current.title}</div>
            <div className={styles.slideContent}>
              {current.content.split('\n').map((line, idx) => (
                line.trim() && (
                  <div key={idx} className={styles.bullet}>
                    • {line.trim()}
                  </div>
                )
              ))}
            </div>
            {current.image_url && (
              <div className={styles.slideImage}>
                <img src={current.image_url} alt={current.title} />
              </div>
            )}
            {!current.image_url && current.image_prompt && (
              <div className={styles.imagePlaceholder}>
                <FaImage />
                <span>Изображение будет сгенерировано</span>
              </div>
            )}
          </div>
        </div>

        <button onClick={nextSlide} className={styles.navButton} disabled={currentSlide === slides.length - 1}>
          <FaChevronRight />
        </button>
      </div>

      <div className={styles.thumbnails}>
        {slides.map((slide, idx) => (
          <div
            key={idx}
            className={`${styles.thumbnail} ${idx === currentSlide ? styles.active : ''}`}
            onClick={() => setCurrentSlide(idx)}
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