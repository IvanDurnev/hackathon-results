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
            <h1>Генератор презентаций</h1>
            <p>Автоматическая генерация презентаций с помощью нейросетей</p>
          </div>
        </div>
        <div className={styles.badges}>
          <a className={styles.badge} href='https://amur.rt.ru/'>Ростелеком</a>
        </div>
      </div>
    </header>
  );
};

export default Header;