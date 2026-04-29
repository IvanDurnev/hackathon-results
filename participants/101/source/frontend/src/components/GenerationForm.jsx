import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import Select from 'react-select';
import { FaUpload, FaFile, FaTrash, FaImage, FaRegFileAlt, FaTimes, FaExclamationTriangle } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import styles from './GenerationForm.module.scss';

const styleOptions = [
  { value: 'corporate', label: 'Корпоративный', icon: '🏢', description: 'Строгий, деловой стиль' },
  { value: 'creative', label: 'Креативный', icon: '🎨', description: 'Яркий, нестандартный подход' },
  { value: 'minimalist', label: 'Минималистичный', icon: '✨', description: 'Лаконичный, современный дизайн' }
];

const toneOptions = [
  { value: 'professional', label: 'Профессиональный', icon: '💼', description: 'Деловой, официальный тон' },
  { value: 'friendly', label: 'Дружелюбный', icon: '😊', description: 'Доступный, располагающий стиль' },
  { value: 'academic', label: 'Академический', icon: '📚', description: 'Научный, структурированный подход' }
];

const templateOptions = [
  { value: 1, label: 'Двухколончная', icon: '📄', description: 'Текст слева, изображение справа' },
  { value: 2, label: 'Полноширинная', icon: '📰', description: 'Текст на всю ширину с изображением внизу' },
  { value: 3, label: 'Сетка', icon: '🔲', description: 'Блочная разметка с несколькими элементами' }
];

const STORAGE_KEY = 'presentationFormSettings';

const GenerationForm = ({ onSubmit, loading }) => {
  const navigate = useNavigate();
  
  // Состояние формы
  const [prompt, setPrompt] = useState('');
  const [numSlides, setNumSlides] = useState(10);
  const [selectedStyle, setSelectedStyle] = useState(styleOptions[0]);
  const [selectedTone, setSelectedTone] = useState(toneOptions[0]);
  const [selectedTemplate, setSelectedTemplate] = useState(templateOptions[0]);
  const [includeImages, setIncludeImages] = useState(true);
  const [document, setDocument] = useState(null);
  
  // Состояние ошибок и уведомлений
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [validationError, setValidationError] = useState('');

  // Загрузка сохраненных настроек при монтировании компонента
  useEffect(() => {
    const savedSettings = localStorage.getItem(STORAGE_KEY);
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        
        // Восстанавливаем настройки
        if (settings.prompt) setPrompt(settings.prompt);
        if (settings.numSlides) setNumSlides(settings.numSlides);
        if (settings.style) {
          const style = styleOptions.find(s => s.value === settings.style);
          if (style) setSelectedStyle(style);
        }
        if (settings.tone) {
          const tone = toneOptions.find(t => t.value === settings.tone);
          if (tone) setSelectedTone(tone);
        }
        if (settings.template) {
          const template = templateOptions.find(t => t.value === settings.template);
          if (template) setSelectedTemplate(template);
        }
        if (settings.includeImages !== undefined) setIncludeImages(settings.includeImages);
      } catch (e) {
        console.error('Ошибка загрузки настроек:', e);
      }
    }
  }, []);

  // Сохранение настроек в localStorage при их изменении
  const saveSettings = useCallback((newSettings) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));
    } catch (e) {
      console.error('Ошибка сохранения настроек:', e);
    }
  }, []);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles[0]) {
      setDocument(acceptedFiles[0]);
      clearError('document');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    disabled: loading,
    onDropRejected: (rejectedFiles) => {
      setErrors({...errors, document: 'Допустимы только PDF и DOCX файлы'});
    }
  });

  const clearError = (field) => {
    const newErrors = {...errors};
    delete newErrors[field];
    setErrors(newErrors);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!prompt.trim()) {
      newErrors.prompt = 'Заполните тему презентации';
    } else if (prompt.trim().length < 3) {
      newErrors.prompt = 'Минимум 3 символа';
    }

    if (numSlides < 1 || numSlides > 20) {
      newErrors.numSlides = 'Количество слайдов должно быть от 1 до 20';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePromptChange = (e) => {
    const value = e.target.value;
    setPrompt(value);
    clearError('prompt');
    
    // Сохраняем в localStorage
    const settings = {
      prompt: value,
      numSlides,
      style: selectedStyle.value,
      tone: selectedTone.value,
      template: selectedTemplate.value,
      includeImages
    };
    saveSettings(settings);
  };

  const handleNumSlidesChange = (e) => {
    const value = Number(e.target.value);
    setNumSlides(value);
    clearError('numSlides');
    
    // Сохраняем в localStorage
    const settings = {
      prompt,
      numSlides: value,
      style: selectedStyle.value,
      tone: selectedTone.value,
      template: selectedTemplate.value,
      includeImages
    };
    saveSettings(settings);
  };

  const handleStyleChange = (option) => {
    setSelectedStyle(option);
    const settings = {
      prompt,
      numSlides,
      style: option.value,
      tone: selectedTone.value,
      template: selectedTemplate.value,
      includeImages
    };
    saveSettings(settings);
  };

  const handleToneChange = (option) => {
    setSelectedTone(option);
    const settings = {
      prompt,
      numSlides,
      style: selectedStyle.value,
      tone: option.value,
      template: selectedTemplate.value,
      includeImages
    };
    saveSettings(settings);
  };

  const handleTemplateChange = (option) => {
    setSelectedTemplate(option);
    const settings = {
      prompt,
      numSlides,
      style: selectedStyle.value,
      tone: selectedTone.value,
      template: option.value,
      includeImages
    };
    saveSettings(settings);
  };

  const handleIncludeImagesChange = (e) => {
    const value = e.target.checked;
    setIncludeImages(value);
    const settings = {
      prompt,
      numSlides,
      style: selectedStyle.value,
      tone: selectedTone.value,
      template: selectedTemplate.value,
      includeImages: value
    };
    saveSettings(settings);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setValidationError('Пожалуйста, исправьте ошибки в форме');
      setTimeout(() => setValidationError(''), 5000);
      return;
    }

    const request = {
      prompt: prompt.trim(),
      numSlides: numSlides,
      style: selectedStyle.value,
      tone: selectedTone.value,
      templateId: selectedTemplate.value,
      includeImages: includeImages,
      document: document || undefined
    };

    try {
      setValidationError('');
      await onSubmit(request);
      setSuccessMessage('Презентация успешно создана!');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (error) {
      const errorMsg = error.message || 'Ошибка при генерации презентации';
      setValidationError(errorMsg);
      // Не очищаем форму при ошибке - настройки остаются сохраненными
      setTimeout(() => setValidationError(''), 5000);
    }
  };

  const removeDocument = () => {
    setDocument(null);
    clearError('document');
  };

  const handleNavigateToEditor = () => {
    const testSlides = [
      {
        id: 1,
        title: 'Пример слайда 1',
        content: 'Это содержимое примерного слайда',
        image_url: null
      },
      {
        id: 2,
        title: 'Пример слайда 2',
        content: 'Вы можете заменить эти данные реальными',
        image_url: null
      }
    ];

    const testSessionId = `test_${Date.now()}`;

    navigate('/editor', {
      state: {
        slides: testSlides,
        sessionId: testSessionId
      }
    });
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
      {/* Сообщения об ошибках и успехе */}
      {validationError && (
        <div className={`${styles.message} ${styles.error}`}>
          <FaExclamationTriangle className={styles.messageIcon} />
          <div className={styles.messageContent}>
            <div className={styles.messageText}>{validationError}</div>
          </div>
          <button 
            type="button"
            className={styles.messageClose}
            onClick={() => setValidationError('')}
          >
            <FaTimes />
          </button>
        </div>
      )}

      {successMessage && (
        <div className={`${styles.message} ${styles.success}`}>
          <div className={styles.messageIcon}>✓</div>
          <div className={styles.messageContent}>
            <div className={styles.messageText}>{successMessage}</div>
          </div>
          <button 
            type="button"
            className={styles.messageClose}
            onClick={() => setSuccessMessage('')}
          >
            <FaTimes />
          </button>
        </div>
      )}

      <div className={styles.section}>
        <label className={styles.label}>
          <FaRegFileAlt className={styles.labelIcon} />
          Тема презентации *
        </label>
        <textarea
          className={`${styles.textarea} ${errors.prompt ? styles.error : ''}`}
          value={prompt}
          onChange={handlePromptChange}
          placeholder="Например: Презентация о развитии искусственного интеллекта в телекоммуникациях..."
          rows={4}
          disabled={loading}
          required
        />
        {errors.prompt && <div className={styles.fieldError}>{errors.prompt}</div>}
      </div>

      <div className={styles.section}>
        <label className={styles.label}>
          <FaUpload className={styles.labelIcon} />
          Дополнительный документ (опционально)
        </label>
        <div
          {...getRootProps()}
          className={`${styles.dropzone} ${isDragActive ? styles.active : ''} ${document ? styles.hasFile : ''} ${errors.document ? styles.error : ''}`}
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
        {errors.document && <div className={styles.fieldError}>{errors.document}</div>}
      </div>

      <div className={styles.row}>
        <div className={styles.section}>
          <label className={styles.label}>Количество слайдов (1-20) *</label>
          <input
            type="range"
            min="1"
            max="20"
            value={numSlides}
            onChange={handleNumSlidesChange}
            disabled={loading}
            className={styles.slider}
          />
          <div className={styles.sliderValue}>{numSlides} слайдов</div>
          {errors.numSlides && <div className={styles.fieldError}>{errors.numSlides}</div>}
        </div>

        <div className={styles.section}>
          <label className={styles.label}>Стиль оформления *</label>
          <Select
            options={styleOptions}
            value={selectedStyle}
            onChange={handleStyleChange}
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
      </div>

      <div className={styles.row}>
        <div className={styles.section}>
          <label className={styles.label}>Тон повествования *</label>
          <Select
            options={toneOptions}
            value={selectedTone}
            onChange={handleToneChange}
            formatOptionLabel={formatOption}
            isDisabled={loading}
            className={styles.reactSelect}
            classNamePrefix="select"
          />
        </div>

        <div className={styles.section}>
          <label className={styles.label}>Шаблон разметки *</label>
          <Select
            options={templateOptions}
            value={selectedTemplate}
            onChange={handleTemplateChange}
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
            onChange={handleIncludeImagesChange}
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

      <button
        type="button"
        className={styles.submitButton}
        onClick={handleNavigateToEditor}
      >
        Перейти в редактор
      </button>
    </form>
  );
};

export default GenerationForm;