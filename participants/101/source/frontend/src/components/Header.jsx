import React from 'react';
import { FaRobot } from 'react-icons/fa';
import styles from './Header.module.scss';

const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logo}>
          <FaRobot className={styles.logoIcon} />
          <div>
            <h1>AI Presentation Generator</h1>
            <p>Автоматическая генерация презентаций с помощью нейросетей</p>
          </div>
        </div>
        <div className={styles.badges}>
          <span className={styles.badge}>Ростелеком</span>
          <span className={styles.badge}>Leopold LLM</span>
          <span className={styles.badge}>Yandex ART</span>
        </div>
      </div>
    </header>
  );
};

export default Header;