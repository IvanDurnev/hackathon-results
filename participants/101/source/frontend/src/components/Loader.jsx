import React from 'react';
import styles from './Loader.module.scss';

const Loader = ({ message = 'Генерация презентации...' }) => {
  const steps = [
    '📝 Анализ запроса',
    '🧠 Генерация структуры',
    '🎨 Создание слайдов',
    '📊 Сборка презентации'
  ];

  return (
    <div className={styles.overlay}>
      <div className={styles.container}>
        <div className={styles.spinner}></div>
        <div className={styles.text}>
          <h3>{message}</h3>
          <p>Это может занять несколько секунд</p>
        </div>
        <div className={styles.steps}>
          {steps.map((step, index) => (
            <div key={index} className={styles.step}>
              {step}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Loader;