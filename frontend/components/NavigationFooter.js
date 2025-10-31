import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import styles from '../styles/PageAccueil.module.css';

export default function NavigationFooter({ onScanClick }) {
  const router = useRouter();
  const [activeIcon, setActiveIcon] = useState('scan'); // 'scan', 'ampoule', 'bot'

  // Déterminer l'icône active en fonction de la route
  useEffect(() => {
    const path = router.pathname;
    if (path === '/home') {
      setActiveIcon('ampoule');
    } else {
      setActiveIcon('scan');
    }
  }, [router.pathname]);

  const handleAmpouleClick = () => {
    setActiveIcon('ampoule');
    router.push('/home');
  };

  const handleScanClick = () => {
    setActiveIcon('scan');
    // Si on est déjà sur la page scan et qu'une fonction de capture est fournie
    if (router.pathname === '/' && onScanClick) {
      onScanClick();
    } else {
      router.push('/');
    }
  };

  const handleBotClick = () => {
    // Le bouton bot reste mais ne fait rien pour l'instant
    // Vous pouvez ajouter une fonction plus tard
  };

  // Déterminer quelle icône est au centre
  const centerIcon = activeIcon;
  const leftIcon = centerIcon === 'ampoule' ? 'scan' : 'ampoule';
  const rightIcon = centerIcon === 'bot' ? 'scan' : 'bot';

  return (
    <footer className={styles.footer}>
      <button 
        className={activeIcon === 'ampoule' ? styles.navButton + ' ' + styles.centerButton : styles.navButton}
        onClick={handleAmpouleClick}
      >
        <img 
          src='/ampoule.svg' 
          alt='Suggestions' 
          width={activeIcon === 'ampoule' ? "38" : "35"} 
          height={activeIcon === 'ampoule' ? "38" : "35"}
          style={{ 
            filter: activeIcon === 'ampoule' 
              ? 'brightness(0) saturate(100%) invert(59%) sepia(11%) saturate(2072%) hue-rotate(75deg) brightness(95%) contrast(81%)' 
              : 'brightness(0) invert(1)' 
          }}
        />
      </button>

      <button 
        className={activeIcon === 'scan' ? styles.navButton + ' ' + styles.centerButton : styles.navButton}
        onClick={handleScanClick}
      >
        <img 
          src='/scan.svg' 
          alt='Scanner' 
          width={activeIcon === 'scan' ? "38" : "35"} 
          height={activeIcon === 'scan' ? "38" : "35"}
          style={{ 
            filter: activeIcon === 'scan' 
              ? 'brightness(0) saturate(100%) invert(59%) sepia(11%) saturate(2072%) hue-rotate(75deg) brightness(95%) contrast(81%)' 
              : 'brightness(0) invert(1)' 
          }}
        />
      </button>

      <button 
        className={activeIcon === 'bot' ? styles.navButton + ' ' + styles.centerButton : styles.navButton}
        onClick={handleBotClick}
      >
        <img 
          src='/bot.svg' 
          alt='Chatbot' 
          width={activeIcon === 'bot' ? "38" : "35"} 
          height={activeIcon === 'bot' ? "38" : "35"}
          style={{ 
            filter: activeIcon === 'bot' 
              ? 'brightness(0) saturate(100%) invert(59%) sepia(11%) saturate(2072%) hue-rotate(75deg) brightness(95%) contrast(81%)' 
              : 'brightness(0) invert(1)' 
          }}
        />
      </button>
    </footer>
  );
}
