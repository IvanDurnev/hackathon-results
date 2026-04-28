import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Select from 'react-select';
import { FaUpload, FaFile, FaTrash, FaImage, FaRegFileAlt } from 'react-icons/fa';
import styles from './GenerationForm.module.scss';

const styleOptions = [
  { value: 'corporate', label: 'Корпоративный', icon: '🏢', description: 'Строгий, деловой стиль' },
  { value: 'creative', label: 'Креативный', icon: '🎨', description: 'Яркий, нестандартный подход' },
  { value: 'minimal', label: 'Минималистичный', icon: '✨', description: 'Лаконичный, современный дизайн' }
];

const toneOptions = [
  { value: 'professional', label: 'Профессиональный', icon: '💼', description: 'Деловой, официальный тон' },
  { value: 'friendly', label: 'Дружелюбный', icon: '😊', description: 'Доступный, располагающий стиль' },
  { value: 'academic', label: 'Академический', icon: '📚', description: 'Научный, структурированный подход' }
];

const GenerationForm = ({ onSubmit, loading }) => {
  const [prompt, setPrompt] = useState('');
  const [numSlides, setNumSlides] = useState(10);
  const [selectedStyle, setSelectedStyle] = useState(styleOptions[0]);
  const [selectedTone, setSelectedTone] = useState(toneOptions[0]);
  const [includeImages, setIncludeImages] = useState(true);
  const [document, setDocument] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles[0]) {
      setDocument(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    disabled: loading
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const request = {
      prompt: prompt.trim(),
      numSlides: numSlides,
      style: selectedStyle.value,
      tone: selectedTone.value,
      includeImages: includeImages,
      document: document || undefined
    };
    onSubmit(request);
  };

  const removeDocument = () => {
    setDocument(null);
  };

  const formatOption = ({ icon, label, description }) => (
    <div className={styles.selectOption}>
      <span className={styles.optionIcon}>{icon}</span>
      <div>
        <div className={styles.optionLabel}>{label}</div>
        <div className={styles.optionDescription}>{description}</div>
      </div>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.section}>
        <label className={styles.label}>
          <FaRegFileAlt className={styles.labelIcon} />
          Тема презентации
        </label>
        <textarea
          className={styles.textarea}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Например: Презентация о развитии искусственного интеллекта в телекоммуникациях..."
          rows={4}
          disabled={loading}
          required
        />
      </div>

      <div className={styles.section}>
        <label className={styles.label}>
          <FaUpload className={styles.labelIcon} />
          Дополнительный документ (опционально)
        </label>
        <div
          {...getRootProps()}
          className={`${styles.dropzone} ${isDragActive ? styles.active : ''} ${document ? styles.hasFile : ''}`}
        >
          <input {...getInputProps()} />
          {document ? (
            <div className={styles.fileInfo}>
              <FaFile />
              <span>{document.name}</span>
              <button type="button" onClick={removeDocument} className={styles.removeFile}>
                <FaTrash />
              </button>
            </div>
          ) : (
            <div className={styles.dropzoneContent}>
              <FaUpload className={styles.uploadIcon} />
              <p>Перетащите файл PDF или DOCX сюда</p>
              <span className={styles.hint}>или кликните для выбора</span>
            </div>
          )}
        </div>
      </div>

      <div className={styles.row}>
        <div className={styles.section}>
          <label className={styles.label}>Количество слайдов (1-20)</label>
          <input
            type="range"
            min="1"
            max="20"
            value={numSlides}
            onChange={(e) => setNumSlides(Number(e.target.value))}
            disabled={loading}
            className={styles.slider}
          />
          <div className={styles.sliderValue}>{numSlides} слайдов</div>
        </div>

        <div className={styles.section}>
          <label className={styles.label}>Стиль оформления</label>
          <Select
            options={styleOptions}
            value={selectedStyle}
            onChange={setSelectedStyle}
            formatOptionLabel={formatOption}
            isDisabled={loading}
            className={styles.reactSelect}
            classNamePrefix="select"
            styles={{
              control: (base) => ({
                ...base,
                borderRadius: '12px',
                borderColor: '#e0e0e0',
                '&:hover': { borderColor: '#667eea' }
              })
            }}
          />
        </div>

        <div className={styles.section}>
          <label className={styles.label}>Тон повествования</label>
          <Select
            options={toneOptions}
            value={selectedTone}
            onChange={setSelectedTone}
            formatOptionLabel={formatOption}
            isDisabled={loading}
            className={styles.reactSelect}
            classNamePrefix="select"
          />
        </div>
      </div>

      <div className={styles.checkboxGroup}>
        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={includeImages}
            onChange={(e) => setIncludeImages(e.target.checked)}
            disabled={loading}
          />
          <FaImage />
          <span>Генерировать изображения для слайдов (Yandex ART)</span>
        </label>
      </div>

      <button type="submit" className={styles.submitButton} disabled={loading || !prompt.trim()}>
        {loading ? (
          <div className={styles.buttonLoading}>
            <div className={styles.buttonSpinner}></div>
            <span>Генерация...</span>
          </div>
        ) : (
          <span>Создать презентацию</span>
        )}
      </button>
    </form>
  );
};

export default GenerationForm;