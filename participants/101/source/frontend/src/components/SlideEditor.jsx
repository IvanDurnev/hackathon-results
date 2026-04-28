import React, { useState } from 'react';
import { FaSave, FaTimes } from 'react-icons/fa';
import styles from './SlideEditor.module.scss';

const SlideEditor = ({ slide, index, onSave, onClose }) => {
  const [editedSlide, setEditedSlide] = useState(slide);

  const handleSave = () => {
    onSave(index, editedSlide);
    onClose();
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h3>Редактирование слайда {index + 1}</h3>
          <button onClick={onClose} className={styles.closeButton}>
            <FaTimes />
          </button>
        </div>

        <div className={styles.content}>
          <div className={styles.field}>
            <label>Заголовок</label>
            <input
              type="text"
              value={editedSlide.title}
              onChange={(e) => setEditedSlide({ ...editedSlide, title: e.target.value })}
              className={styles.input}
            />
          </div>

          <div className={styles.field}>
            <label>Содержание</label>
            <textarea
              value={editedSlide.content}
              onChange={(e) => setEditedSlide({ ...editedSlide, content: e.target.value })}
              rows={8}
              className={styles.textarea}
            />
          </div>

          <div className={styles.field}>
            <label>Промпт для изображения</label>
            <input
              type="text"
              value={editedSlide.image_prompt || ''}
              onChange={(e) => setEditedSlide({ ...editedSlide, image_prompt: e.target.value })}
              className={styles.input}
              placeholder="Описание для генерации изображения"
            />
          </div>
        </div>

        <div className={styles.footer}>
          <button onClick={onClose} className={styles.cancelButton}>Отмена</button>
          <button onClick={handleSave} className={styles.saveButton}>
            <FaSave /> Сохранить
          </button>
        </div>
      </div>
    </div>
  );
};

export default SlideEditor;