import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import TrueFocus from '../components/TrueFocus';
import styles from '../styles/PageAccueil.module.css';

export default function PageAccueil() {
  const router = useRouter();
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const handleScanClick = async () => {
    setShowCamera(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment', // Caméra arrière sur mobile
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Erreur accès caméra:', err);
      alert('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
      setShowCamera(false);
    }
  };

  const handleCloseCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setShowCamera(false);
  };

  // Nettoyage quand le composant est démonté
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const handleMenuClick = () => {
    // Navigation vers menu/historique
    console.log('Menu clicked');
  };

  const handleAddClick = () => {
    // Navigation vers ajout manuel
    console.log('Add clicked');
  };

  const handleSearchClick = () => {
    // Navigation vers recherche
    console.log('Search clicked');
  };

  return (
    <div className={styles.container}>
      {/* Header avec profil */}
      <header className={styles.header}>
        <div className={styles.profileIcon}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
          </svg>
        </div>
        <div style={{ width: '40px' }}></div>
        <button className={styles.moreButton}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="5" r="1.5" fill="currentColor"/>
            <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
            <circle cx="12" cy="19" r="1.5" fill="currentColor"/>
          </svg>
        </button>
      </header>

      {/* Animation TrueFocus entre header et main */}
      <div className={styles.trueFocusSection}>
        <TrueFocus 
          sentence="Assiette prête?"
          manualMode={false}
          blurAmount={5}
          borderColor="#66BB6A"
          glowColor="rgba(102, 187, 106, 0.6)"
          animationDuration={2}
          pauseBetweenAnimations={1}
        />
      </div>

      {/* Zone principale - Photo ou Scan */}
      <main className={styles.mainContent}>
        {!showCamera ? (
          <div className={styles.scanPrompt}>
            <div className={styles.focusFrame}>
              <span className={styles.corner + ' ' + styles.topLeft}></span>
              <span className={styles.corner + ' ' + styles.topRight}></span>
              <span className={styles.corner + ' ' + styles.bottomLeft}></span>
              <span className={styles.corner + ' ' + styles.bottomRight}></span>
            </div>
            <p className={styles.scanText}>Scanne moi</p>
            <button className={styles.scanButton} onClick={handleScanClick}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
            </button>
          </div>
        ) : (
          <div className={styles.cameraView}>
            <video 
              ref={videoRef}
              className={styles.video} 
              autoPlay 
              playsInline
            ></video>
            <div className={styles.scanOverlay}>
              <div className={styles.focusFrame}>
                <span className={styles.corner + ' ' + styles.topLeft}></span>
                <span className={styles.corner + ' ' + styles.topRight}></span>
                <span className={styles.corner + ' ' + styles.bottomLeft}></span>
                <span className={styles.corner + ' ' + styles.bottomRight}></span>
              </div>
              <button className={styles.closeCamera} onClick={handleCloseCamera}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Indicateur du produit scanné */}
        <div className={styles.productIndicator}>
          <div className={styles.productIcon}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="8" r="4"/>
              <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
            </svg>
          </div>
          <div className={styles.productInfo}>
            <span className={styles.productName}>Mes repas</span>
          </div>
          <button className={styles.addProductButton}>
            +
          </button>
        </div>
      </main>

      {/* Footer avec navigation */}
      <footer className={styles.footer}>
        <button className={styles.navButton} onClick={handleMenuClick}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <button className={styles.navButton + ' ' + styles.centerButton} onClick={handleAddClick}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>

        <button className={styles.navButton} onClick={handleSearchClick}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
        </button>
      </footer>
    </div>
  );
}
