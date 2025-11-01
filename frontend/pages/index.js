import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../utils/api';
import TrueFocus from '../components/TrueFocus';
import NavigationFooter from '../components/NavigationFooter';
import styles from '../styles/PageAccueil.module.css';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading, userId, logout } = useAuth();
  const [showCamera, setShowCamera] = useState(true);
  const [facingMode, setFacingMode] = useState('environment'); // 'environment' pour arrière, 'user' pour avant
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [editableAliments, setEditableAliments] = useState([]);
  const [showSuggestionCard, setShowSuggestionCard] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Vérifier l'authentification au chargement
  useEffect(() => {
    const checkAuthAndProfile = async () => {
      if (isLoading) return;
      
      if (!isAuthenticated) {
        // Pas de session, rediriger vers la page d'accueil
        router.push('/welcome');
        return;
      }

      // Vérifier si le profil est complété
      if (userId) {
        try {
          const data = await apiClient.get(`/api/profile/check?user_id=${userId}`);
          
          if (!data.profile_completed) {
            // Profil non complété, rediriger vers l'onboarding
            router.push('/onboarding-new');
            return;
          }
        } catch (err) {
          console.log('Error checking profile:', err);
          // Continue even if there's an error
        }
      }
    };

    checkAuthAndProfile();
  }, [router, isAuthenticated, isLoading, userId]);

  // Fonction pour démarrer la caméra
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setShowCamera(false);
    }
  };

  // Ouvrir la caméra automatiquement au chargement
  useEffect(() => {
    if (!isAuthenticated || isLoading) return;
    
    startCamera();

    // Nettoyer quand le composant est démonté
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isAuthenticated, isLoading, facingMode]);

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
      console.error('Camera access error:', err);
      alert('Unable to access the camera. Please check permissions.');
      setShowCamera(false);
    }
  };

  const handleCloseCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    setShowCamera(false);
  };

  const handleFlipCamera = () => {
    // Inverser entre caméra avant et arrière
    setFacingMode(prevMode => prevMode === 'environment' ? 'user' : 'environment');
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
    // Navigation vers la page des statistiques
    router.push('/home');
  };

  const handleAddClick = () => {
    // Navigation vers les suggestions
    router.push('/suggestion');
  };

  const handleSearchClick = () => {
    // Navigation vers recherche
    console.log('Search clicked');
  };

  const handleLogout = () => {
    logout();
  };

  const handleProfileClick = () => {
    // Rediriger vers la page d'onboarding pour modifier les réponses
    router.push('/onboarding-new');
  };

  const handleGalleryClick = () => {
    // Ouvrir le sélecteur de fichiers
    fileInputRef.current?.click();
  };

  const handleCapturePhoto = () => {
    // Capturer une photo depuis le flux vidéo
    if (videoRef.current) {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Arrêter le flux vidéo
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      // Convertir en blob
      canvas.toBlob((blob) => {
        if (blob) {
          const imageUrl = URL.createObjectURL(blob);
          setSelectedImage(imageUrl);
          // Stocker le blob pour l'envoyer plus tard lors de la validation
          window.capturedBlob = blob;
          console.log('Photo capturée');
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const handleValidatePhoto = () => {
    // Envoyer la photo capturée pour analyse
    if (window.capturedBlob) {
      const file = new File([window.capturedBlob], 'captured-photo.jpg', { type: 'image/jpeg' });
      
      // Lancer l'analyse (ne pas revenir à la caméra)
      analyzeImage(file);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const imageUrl = URL.createObjectURL(file);
      // Store the file in window for later validation (same as camera capture)
      window.capturedBlob = file;
      setSelectedImage(imageUrl);
      console.log('Image sélectionnée:', file.name);
      // Don't analyze immediately - wait for user to click validate button
    }
  };

  const analyzeImage = async (file) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const data = await apiClient.post('/api/analyze/plate', formData);
      
      console.log('Résultat analyse:', data);
      
      // Vérifier si des aliments ont été détectés
      if (data.aliments && data.aliments.length > 0) {
        setAnalysisResult(data);
        setEditableAliments(data.aliments || []);
        console.log(`${data.nombre_aliments} food item(s) detected!`);
      } else {
        // Aucun aliment détecté - revenir à la caméra
        setErrorMessage('No food detected. Please try again with a better photo.');
        setSelectedImage(null);
        setAnalysisResult(null);
        setEditableAliments([]);
        startCamera();
        
        // Effacer le message d'erreur après 3 secondes
        setTimeout(() => setErrorMessage(null), 3000);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setErrorMessage('Error analyzing image. Please try again.');
      setSelectedImage(null);
      setAnalysisResult(null);
      setEditableAliments([]);
      startCamera();
      
      // Effacer le message d'erreur après 3 secondes
      setTimeout(() => setErrorMessage(null), 3000);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAlimentChange = (index, field, value) => {
    const updatedAliments = [...editableAliments];
    updatedAliments[index][field] = value;
    setEditableAliments(updatedAliments);
  };

  const handleValidateAliments = async () => {
  setIsAnalyzing(false);
  setSelectedImage(null);
  setAnalysisResult(null);
  setEditableAliments([]);
  setIsAnalyzing(false);
    if (editableAliments.length === 0) {
      setErrorMessage('No food items to validate.');
      setTimeout(() => setErrorMessage(null), 3000);
      return;
    }

    // Reset UI and return to camera immediately
    setIsAnalyzing(false);
    setSelectedImage(null);
    setAnalysisResult(null);
    setEditableAliments([]);
    startCamera();

    // Launch API call in background
    setTimeout(async () => {
      try {
        await apiClient.post('/api/analyze/nutrients', editableAliments);
        // Optionally show a success toast
      } catch (error) {
        console.error('Validation error:', error);
        // Optionally show an error toast
      }
    }, 100);
  };

  const handleAddAliment = () => {
    setEditableAliments([...editableAliments, { name: '', estimated_quantity: 0 }]);
  };

  const handleDeleteAliment = (index) => {
    const updatedAliments = editableAliments.filter((_, i) => i !== index);
    setEditableAliments(updatedAliments);
  };

  return (
    <div className={styles.container}>
      {/* Header avec profil */}
      <header className={styles.header}>
        <button className={styles.profileIcon} onClick={handleProfileClick} title="Edit my profile">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
          </svg>
        </button>
        <div style={{ width: '40px' }}></div>
        <button className={styles.logoutButton} onClick={handleLogout} title="Logout">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </header>

      {/* Animation TrueFocus entre header et main */}
      <div className={styles.trueFocusSection}>
        <TrueFocus 
          sentence="Plate ready?"
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
        {/* Message d'erreur discret en haut */}
        {errorMessage && (
          <div className={styles.errorToast}>
            {errorMessage}
          </div>
        )}

        {/* Input file caché pour sélectionner une image */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        {/* État : En cours d'analyse */}
        {isAnalyzing && selectedImage && (
          <div className={styles.scanContainer}>
            <div className={styles.cameraView}>
              <img src={selectedImage} alt="Analyzing" className={styles.capturedImage} />
              <div className={styles.analyzingOverlay}>
                <div className={styles.spinner}></div>
                <p className={styles.analyzingText}>Analysing plate...</p>
              </div>
            </div>
          </div>
        )}
        
        {/* État : Photo capturée, en attente de validation */}
        {selectedImage && !isAnalyzing && !analysisResult && (
          // Affichage de la photo capturée dans le même bloc que la caméra
          <div className={styles.scanContainer}>
            <div className={styles.cameraView}>
              <img src={selectedImage} alt="Captured" className={styles.capturedImage} />
              <button className={styles.closeImage} onClick={() => {
                setSelectedImage(null);
                setAnalysisResult(null);
                setEditableAliments([]);
                // Redémarrer la caméra
                startCamera();
              }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
              {/* Bouton de validation au centre en bas */}
              <button className={styles.validatePhotoButton} onClick={handleValidatePhoto}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </button>
            </div>
            <div className={styles.buttonGroup}>
              <button className={styles.scanButton} onClick={handleCapturePhoto}>
                <img src="/Calendar.svg" alt="Calendar" width="32" height="32" />
              </button>
              <button className={styles.galleryButton} onClick={handleGalleryClick}>
                <img src="/picture.svg" alt="Gallery" width="32" height="32" />
              </button>
            </div>
          </div>
        )}
        
        {/* État : Résultats de l'analyse - Afficher uniquement les résultats sans la caméra */}
        {analysisResult && !isAnalyzing && (
          <div className={styles.analysisContainer}>
            <div className={styles.imageSection}>
              <img src={selectedImage} alt="Selected image" className={styles.selectedImage} />
              
              {/* Bouton croix pour revenir au scannage */}
              <button className={styles.closeImage} onClick={() => {
                setSelectedImage(null);
                setAnalysisResult(null);
                setEditableAliments([]);
                // Redémarrer la caméra
                startCamera();
              }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            
            {/* Panneau d'édition des aliments */}
            <div className={styles.editPanel}>
              <div className={styles.editHeader}>
                <h3>{editableAliments.length} food item(s) detected</h3>
                <p className={styles.editSubtitle}>Edit quantities if needed</p>
              </div>
              
              <div className={styles.alimentEditList}>
                {editableAliments.map((aliment, index) => (
                  <div key={index} className={styles.alimentEditItem}>
                    <input
                      type="text"
                      value={aliment.name}
                      onChange={(e) => handleAlimentChange(index, 'name', e.target.value)}
                      className={styles.alimentNameInput}
                      placeholder="Food name"
                    />
                    <div className={styles.quantityControl}>
                      <input
                        type="number"
                        value={aliment.estimated_quantity}
                        onChange={(e) => handleAlimentChange(index, 'estimated_quantity', parseInt(e.target.value) || 0)}
                        className={styles.alimentQuantityInput}
                        min="0"
                      />
                      <span className={styles.unit}>g</span>
                    </div>
                    <button 
                      className={styles.deleteButton}
                      onClick={() => handleDeleteAliment(index)}
                      title="Delete"
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
              
              <div className={styles.editActions}>
                <button 
                  className={styles.addButton} 
                  onClick={handleAddAliment}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  Add food item
                </button>
                <button 
                  className={styles.validateButton} 
                  onClick={handleValidateAliments}
                >
                  {'Validate'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* État : Vue caméra normale (pas de photo sélectionnée, pas de résultats) */}
        {!selectedImage && !analysisResult && !isAnalyzing && (
          <div className={styles.scanContainer}>
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
                <button className={styles.flipCamera} onClick={handleFlipCamera}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                    <path d="M17 2L21 6L17 10"/>
                    <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
                    <path d="M7 22L3 18L7 14"/>
                    <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
                  </svg>
                </button>
              </div>
            </div>
            <div className={styles.buttonGroup}>
              <button className={styles.scanButton} onClick={handleCapturePhoto}>
                <img src="/Calendar.svg" alt="Calendar" width="32" height="32" />
              </button>
              <button className={styles.galleryButton} onClick={handleGalleryClick}>
                <img src="/picture.svg" alt="Gallery" width="32" height="32" />
              </button>
            </div>
          </div>
        )}

        {/* Bouton vers les suggestions */}
        <div 
          className={`${styles.suggestionCard} ${showSuggestionCard ? styles.visible : ''}`}
          onClick={() => router.push('/suggestion')}
        >
          <div className={styles.suggestionInfo}>
            <span className={styles.suggestionName}>Meal suggestions</span>
            <span className={styles.suggestionSubtext}>View my recommendations</span>
          </div>
          <button className={styles.suggestionArrow}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        </div>
      </main>

      {/* Footer avec navigation */}
      <NavigationFooter onScanClick={handleCapturePhoto} />
    </div>
  );
}
