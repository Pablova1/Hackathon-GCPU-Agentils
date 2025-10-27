import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
import TrueFocus from '../components/TrueFocus';
import styles from '../styles/PageAccueil.module.css';

export default function Home() {
  const router = useRouter();
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [editableAliments, setEditableAliments] = useState([]);
  const [showSuggestionCard, setShowSuggestionCard] = useState(false);

  // Vérifier l'authentification au chargement
  useEffect(() => {
    const checkAuthAndProfile = async () => {
      const token = localStorage.getItem('session_token');
      const userId = localStorage.getItem('user_id');
      
      if (!token) {
        // Pas de session, rediriger vers la page d'authentification
        router.push('/auth');
        return;
      }

      // Vérifier si le profil est complété
      if (userId) {
        try {
          const response = await fetch(`http://localhost:8000/api/profile/check?user_id=${userId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const data = await response.json();
            if (!data.profile_completed) {
              // Profil non complété, rediriger vers l'onboarding
              router.push('/onboarding-new');
              return;
            }
          }
        } catch (err) {
          console.log('Erreur lors de la vérification du profil:', err);
          // Continuer même en cas d'erreur
        }
      }
    };

    checkAuthAndProfile();
  }, [router]);

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
    // Navigation vers les suggestions
    router.push('/suggestion');
  };

  const handleSearchClick = () => {
    // Navigation vers recherche
    console.log('Search clicked');
  };

  const handleLogout = () => {
    // Supprimer les données de session
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('first_name');
    
    // Rediriger vers la page d'authentification
    router.push('/auth');
  };

  const handleProfileClick = () => {
    // Rediriger vers la page d'onboarding pour modifier les réponses
    router.push('/onboarding-new');
  };

  const handleGalleryClick = () => {
    // Ouvrir le sélecteur de fichiers
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const imageUrl = URL.createObjectURL(file);
      setSelectedImage(imageUrl);
      setShowCamera(false);
      console.log('Image sélectionnée:', file.name);
      // Envoyer l'image au backend pour analyse
      analyzeImage(file);
    }
  };

  const analyzeImage = async (file) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);
    
    const token = localStorage.getItem('session_token');
    if (!token) {
      alert('Session expirée. Veuillez vous reconnecter.');
      router.push('/auth');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/analyze/plate', {
        method: 'POST',
        headers: {
          'X-Session-Token': token
        },
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert('Session expirée. Veuillez vous reconnecter.');
          router.push('/auth');
          return;
        }
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      console.log('Résultat analyse:', data);
      setAnalysisResult(data);
      setEditableAliments(data.aliments || []);
      
      // Afficher un message de succès
      if (data.aliments && data.aliments.length > 0) {
        console.log(`${data.nombre_aliments} aliment(s) détecté(s) !`);
      } else {
        alert('Aucun aliment détecté. Veuillez réessayer avec une meilleure photo.');
      }
    } catch (error) {
      console.error('Erreur analyse:', error);
      alert('Erreur lors de l\'analyse de l\'image. Veuillez réessayer.');
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
    if (editableAliments.length === 0) {
      alert('Aucun aliment à valider.');
      return;
    }

    const token = localStorage.getItem('session_token');
    if (!token) {
      alert('Session expirée. Veuillez vous reconnecter.');
      router.push('/auth');
      return;
    }

    try {
      setIsAnalyzing(true);
      
      const response = await fetch('http://localhost:8000/api/analyze/nutrients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': token
        },
        body: JSON.stringify(editableAliments),
      });

      if (!response.ok) {
        if (response.status === 401) {
          alert('Session expirée. Veuillez vous reconnecter.');
          router.push('/auth');
          return;
        }
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      const data = await response.json();
      console.log('Repas validé:', data);
      
      alert(`✅ Repas enregistré avec succès !\n\nID: ${data.meal_id}\n\nSuggestions en cours de génération...`);
      
      // Réinitialiser l'interface
      setSelectedImage(null);
      setAnalysisResult(null);
      setEditableAliments([]);
      
      // Optionnel: rediriger vers la page des suggestions
      // router.push('/suggestion');
      
    } catch (error) {
      console.error('Erreur validation:', error);
      alert('Erreur lors de l\'enregistrement du repas. Veuillez réessayer.');
    } finally {
      setIsAnalyzing(false);
    }
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
        <button className={styles.profileIcon} onClick={handleProfileClick} title="Modifier mon profil">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2">
            <circle cx="12" cy="8" r="4"/>
            <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
          </svg>
        </button>
        <div style={{ width: '40px' }}></div>
        <button className={styles.logoutButton} onClick={handleLogout} title="Déconnexion">
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
        {/* Input file caché pour sélectionner une image */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        {!showCamera && !selectedImage ? (
          <div className={styles.scanPrompt}>
            <div className={styles.focusFrame}>
              <span className={styles.corner + ' ' + styles.topLeft}></span>
              <span className={styles.corner + ' ' + styles.topRight}></span>
              <span className={styles.corner + ' ' + styles.bottomLeft}></span>
              <span className={styles.corner + ' ' + styles.bottomRight}></span>
            </div>
            <p className={styles.scanText}>Scanne moi</p>
            <div className={styles.buttonGroup}>
              <button className={styles.scanButton} onClick={handleScanClick}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
              </button>
              <button className={styles.galleryButton} onClick={handleGalleryClick}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </button>
            </div>
          </div>
        ) : selectedImage ? (
          <div className={styles.analysisContainer}>
            <div className={styles.imageSection}>
              <img src={selectedImage} alt="Image sélectionnée" className={styles.selectedImage} />
              
              {/* Indicateur de chargement pendant l'analyse */}
              {isAnalyzing && (
                <div className={styles.analyzingOverlay}>
                  <div className={styles.spinner}></div>
                  <p className={styles.analyzingText}>Analyse en cours...</p>
                </div>
              )}
              
              <button className={styles.closeImage} onClick={() => {
                setSelectedImage(null);
                setAnalysisResult(null);
                setEditableAliments([]);
              }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            
            {/* Panneau d'édition des aliments */}
            {analysisResult && (
              <div className={styles.editPanel}>
                <div className={styles.editHeader}>
                  <h3>{editableAliments.length} aliment(s) détecté(s)</h3>
                  <p className={styles.editSubtitle}>Modifiez les quantités si nécessaire</p>
                </div>
                
                <div className={styles.alimentEditList}>
                  {editableAliments.map((aliment, index) => (
                    <div key={index} className={styles.alimentEditItem}>
                      <input
                        type="text"
                        value={aliment.name}
                        onChange={(e) => handleAlimentChange(index, 'name', e.target.value)}
                        className={styles.alimentNameInput}
                        placeholder="Nom de l'aliment"
                        disabled={isAnalyzing}
                      />
                      <div className={styles.quantityControl}>
                        <input
                          type="number"
                          value={aliment.estimated_quantity}
                          onChange={(e) => handleAlimentChange(index, 'estimated_quantity', parseInt(e.target.value) || 0)}
                          className={styles.alimentQuantityInput}
                          min="0"
                          disabled={isAnalyzing}
                        />
                        <span className={styles.unit}>g</span>
                      </div>
                      <button 
                        className={styles.deleteButton}
                        onClick={() => handleDeleteAliment(index)}
                        title="Supprimer"
                        disabled={isAnalyzing}
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
                    disabled={isAnalyzing}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="12" y1="5" x2="12" y2="19"></line>
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Ajouter un aliment
                  </button>
                  <button 
                    className={styles.validateButton} 
                    onClick={handleValidateAliments}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? (
                      <>
                        <div className={styles.buttonSpinner}></div>
                        Enregistrement...
                      </>
                    ) : (
                      'Valider'
                    )}
                  </button>
                </div>
              </div>
            )}
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

        {/* Bouton vers les suggestions */}
        <div 
          className={`${styles.suggestionCard} ${showSuggestionCard ? styles.visible : ''}`}
          onClick={() => router.push('/suggestion')}
        >
          <div className={styles.suggestionInfo}>
            <span className={styles.suggestionName}>Suggestions de repas</span>
            <span className={styles.suggestionSubtext}>Voir mes recommandations</span>
          </div>
          <button className={styles.suggestionArrow}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
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

        <button 
          className={styles.navButton + ' ' + styles.centerButton} 
          onClick={handleAddClick}
          onMouseEnter={() => setShowSuggestionCard(true)}
          onMouseLeave={() => setShowSuggestionCard(false)}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#66BB6A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21h6"/>
            <path d="M12 3v3"/>
            <path d="M12 17v1a2 2 0 0 1-2 2h0a2 2 0 0 1-2-2v-1"/>
            <path d="M8 17a5 5 0 1 1 8 0"/>
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
