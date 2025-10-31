import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../utils/api';

export default function Onboarding() {
  const router = useRouter();
  const { isAuthenticated, isLoading, userId, firstName, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [showBodyTypeInfo, setShowBodyTypeInfo] = useState(null);
  const [aiQuestion, setAiQuestion] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  // Vérifier l'authentification et charger les questions
  useEffect(() => {
    const checkAuthAndLoadQuestions = async () => {
      if (isLoading) return;

      // Si pas connecté, rediriger vers la page d'auth
      if (!isAuthenticated || !userId) {
        router.push('/auth');
        return;
      }

      // Charger toutes les questions
      try {
        const questionsData = await apiClient.get('/api/onboarding/questions');
        
        // Filtrer les questions de l'IA (qui commencent généralement par 'ai_' ou ne sont pas standards)
        const standardSlots = [
          'birthDate', 'gender', 'heightCm', 'weightKg', 'bodyType',
          'dietType', 'allergies', 'intolerances', 'foodLikes', 'foodDislikes', 'foodPreferences',
          'treatments', 'medicalHistoryPersonal', 'medicalHistoryFamily', 'birthControl', 'birthControlName',
          'goalMuscleGain', 'goalWeightLoss', 'goalPerformance', 'goalMaintainShape', 'goalDetail',
          'religiousPracticing', 'religiousType',
          'activityLevel', 'sports', 'occupation', 'additionalNotes'
        ];
        
        // Ne garder que les questions standards (pas les questions IA)
        let filteredQuestions = questionsData.questions.filter(q => 
          standardSlots.includes(q.slot)
        );
        
        setQuestions(filteredQuestions);
        
        // Initialiser les réponses vides
        const initialAnswers = {};
        filteredQuestions.forEach(q => {
          initialAnswers[q.slot] = '';
        });

        // Essayer de charger les réponses existantes si le profil est complété
        try {
          const profileData = await apiClient.get(`/api/profile/check?user_id=${userId}`);
          
          console.log('Données de profil reçues:', profileData);
          console.log('Réponses onboarding:', profileData.onboarding_responses);
          
          if (profileData.profile_completed && profileData.onboarding_responses) {
            // Mode modification - charger les réponses existantes
            setIsEditMode(true);
            
            // En mode modification, exclure la question "additionalNotes"
            filteredQuestions = filteredQuestions.filter(q => q.slot !== 'additionalNotes');
            setQuestions(filteredQuestions);
            
            let loadedCount = 0;
            filteredQuestions.forEach(q => {
              if (profileData.onboarding_responses[q.slot]) {
                initialAnswers[q.slot] = profileData.onboarding_responses[q.slot];
                loadedCount++;
              }
            });
            console.log(`${loadedCount} réponses chargées depuis le profil`);
          }
        } catch (err) {
          console.log('Impossible de charger les réponses existantes:', err);
        }
        
        setAnswers(initialAnswers);
        setLoading(false);
      } catch (err) {
        setError('Erreur de connexion au serveur');
        setLoading(false);
      }
    };

    checkAuthAndLoadQuestions();
  }, [router, isAuthenticated, isLoading, userId]);

  // Fonction pour gérer le retour en arrière
  const handleBackClick = () => {
    // Vérifier si on vient de la page auth en regardant le document.referrer
    // ou en vérifiant l'historique du navigateur
    const previousPath = window.history.state?.as || document.referrer;
    
    // Si la page précédente contient '/auth' ou si on est en mode création (pas en mode édition)
    if (previousPath.includes('/auth') || !isEditMode) {
      // Déconnecter l'utilisateur avant de revenir en arrière
      logout();
      router.push('/auth');
    } else {
      // Sinon, simple retour en arrière
      router.back();
    }
  };

  const handleAnswerChange = (slot, value) => {
    setAnswers(prev => ({
      ...prev,
      [slot]: value
    }));
  };

  const handleDateChange = (slot, value) => {
    // Retirer tous les caractères non numériques
    let cleaned = value.replace(/\D/g, '');
    
    // Limiter à 8 chiffres (JJMMAAAA)
    cleaned = cleaned.substring(0, 8);
    
    // Formater avec des /
    let formatted = '';
    if (cleaned.length > 0) {
      formatted = cleaned.substring(0, 2); // JJ
      if (cleaned.length >= 3) {
        formatted += '/' + cleaned.substring(2, 4); // MM
      }
      if (cleaned.length >= 5) {
        formatted += '/' + cleaned.substring(4, 8); // AAAA
      }
    }
    
    setAnswers(prev => ({
      ...prev,
      [slot]: formatted
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    // Valider que toutes les questions obligatoires ont une réponse
    const missingAnswers = questions.filter(q => 
      q.required && (!answers[q.slot] || answers[q.slot] === '')
    );

    if (missingAnswers.length > 0) {
      setError('Please answer all required questions');
      setSubmitting(false);
      return;
    }

    // Convertir les réponses au bon type et filtrer les réponses vides pour les questions optionnelles
    const processedAnswers = {};
    questions.forEach(q => {
      let value = answers[q.slot];
      
      // Si la question est optionnelle et la valeur est vide, ne pas l'inclure
      if (!q.required && (!value || value === '')) {
        return;
      }
      
      if (q.type === 'number') {
        value = parseFloat(value);
        if (isNaN(value)) {
          setError(`Invalid value for: ${q.text}`);
          setSubmitting(false);
          return;
        }
      } else if (q.type === 'date') {
        // Convertir DD/MM/YYYY en YYYY-MM-DD
        const parts = value.split('/');
        if (parts.length === 3) {
          value = `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
      }
      
      processedAnswers[q.slot] = value;
    });

    // Soumettre toutes les réponses
    try {
      const data = await apiClient.post('/api/onboarding/submit-all', {
        user_id: userId,
        answers: processedAnswers
      });

      // Vérifier s'il y a une question IA à poser
      if (data.ai_question) {
        setAiQuestion(data.ai_question);
        setSessionId(data.session_id);
        setSuccess('Great! One more question to personalize your experience...');
        setSubmitting(false);
      } else {
        // Pas de question IA, rediriger directement
        setSuccess('Profile completed successfully! Redirecting...');
        setTimeout(() => {
          router.push('/');
        }, 2000);
      }
    } catch (err) {
      setError(err.data?.detail || err.message || 'Server connection error');
      setSubmitting(false);
    }
  };

  const handleAiAnswerSubmit = async () => {
    if (!aiQuestion || !sessionId) return;
    
    const aiAnswer = answers[aiQuestion.slot];
    if (!aiAnswer || aiAnswer === '') {
      setError('Please answer the question');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const data = await apiClient.post('/api/onboarding/answer', {
        session_id: sessionId,
        slot: aiQuestion.slot,
        value: aiAnswer
      });

      if (data.next_question) {
        // Il y a une autre question IA
        setAiQuestion(data.next_question);
        setAnswers(prev => ({...prev, [aiQuestion.slot]: ''})); // Effacer la réponse précédente
        setSuccess('');
      } else {
        // Terminé, rediriger
        setSuccess('All done! Redirecting...');
        setTimeout(() => {
          router.push('/');
        }, 1500);
      }
    } catch (err) {
      setError(err.data?.detail || err.message || 'Server connection error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkipAiQuestion = () => {
    setSuccess('Profile completed! Redirecting...');
    setTimeout(() => {
      router.push('/');
    }, 1500);
  };

  const renderQuestionInput = (question) => {
    const value = answers[question.slot] || '';

    // Cas spécial pour bodyType avec explications
    if (question.slot === 'bodyType') {
      const bodyTypeInfo = {
        'ectomorphic': '🌿 Ectomorph: Slim silhouette, fast metabolism, difficulty gaining weight',
        'mesomorphic': '💪 Mesomorph: Natural musculature, easy muscle gain, athletic build',
        'endomorphic': '🌰 Endomorph: Larger frame, easy weight gain, slow metabolism',
        'unknown': '❓ I don\'t know'
      };

      return (
        <div style={styles.choicesContainer}>
          {question.choices.map((choice) => (
            <div key={choice} style={{ position: 'relative', display: 'flex', flexDirection: 'column' }}>
              <button
                type="button"
                onClick={() => handleAnswerChange(question.slot, choice)}
                onMouseEnter={() => setShowBodyTypeInfo(choice)}
                onMouseLeave={() => setShowBodyTypeInfo(null)}
                style={{
                  ...styles.choiceButton,
                  ...(value === choice ? styles.choiceButtonSelected : {}),
                  position: 'relative'
                }}
              >
                {choice}
              </button>
              {showBodyTypeInfo === choice && (
                <div style={styles.tooltip}>
                  {bodyTypeInfo[choice]}
                </div>
              )}
            </div>
          ))}
        </div>
      );
    }

    switch (question.type) {
      case 'single_choice':
        return (
          <div style={styles.choicesContainer}>
            {question.choices.map((choice) => (
              <button
                key={choice}
                type="button"
                onClick={() => handleAnswerChange(question.slot, choice)}
                style={{
                  ...styles.choiceButton,
                  ...(value === choice ? styles.choiceButtonSelected : {})
                }}
              >
                {choice}
              </button>
            ))}
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={styles.input}
            placeholder={question.placeholder || "Enter a number"}
            step="any"
            required={question.required}
          />
        );

      case 'date':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleDateChange(question.slot, e.target.value)}
            style={styles.input}
            placeholder={question.placeholder || "DD/MM/YYYY"}
            required={question.required}
            maxLength="10"
          />
        );

      case 'text':
      default:
        return (
          <textarea
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={{...styles.input, minHeight: '80px', resize: 'vertical'}}
            placeholder={question.placeholder || "Your answer..."}
            required={question.required}
          />
        );
    }
  };

  // Organiser les questions par sections
  const organizeQuestions = (questions) => {
    const sections = {
      'Basic Information': ['birthDate', 'gender', 'heightCm', 'weightKg', 'bodyType'],
      'Nutrition': ['dietType', 'allergies', 'intolerances', 'foodLikes', 'foodDislikes', 'foodPreferences'],
      'Health': ['treatments', 'medicalHistoryPersonal', 'medicalHistoryFamily', 'birthControl'],
      'Goals': ['goalMuscleGain', 'goalWeightLoss', 'goalPerformance', 'goalMaintainShape', 'goalDetail'],
      'Religious Restrictions': ['religiousPracticing'],
      'Activity & Lifestyle': ['activityLevel', 'sports', 'occupation', 'additionalNotes']
    };

    const organized = {};
    Object.keys(sections).forEach(sectionName => {
      organized[sectionName] = questions.filter(q => sections[sectionName].includes(q.slot));
    });

    return organized;
  };

  // Fonction pour déterminer si une question doit être affichée
  const shouldShowQuestion = (question) => {
    // birthControlName et religiousType seront affichés inline, pas dans la liste normale
    if (question.slot === 'birthControlName' || question.slot === 'religiousType') {
      return false;
    }
    // Toutes les autres questions sont toujours affichées
    return true;
  };

  // Fonction pour rendre une question avec ses questions conditionnelles
  const renderQuestionBlock = (question, allQuestions) => {
    return (
      <div key={question.slot} style={styles.questionBlock}>
        <label style={styles.questionLabel}>
          {question.text}
          {question.required && <span style={styles.required}> *</span>}
        </label>
        {renderQuestionInput(question)}
        
        {/* Question conditionnelle pour birthControl */}
        {question.slot === 'birthControl' && answers['birthControl'] === 'yes' && (
          <div style={styles.conditionalQuestion}>
            {allQuestions
              .filter(q => q.slot === 'birthControlName')
              .map(subQuestion => (
                <div key={subQuestion.slot} style={{ marginTop: '15px' }}>
                  <label style={styles.questionLabel}>
                    {subQuestion.text}
                    {subQuestion.required && <span style={styles.required}> *</span>}
                  </label>
                  {renderQuestionInput(subQuestion)}
                </div>
              ))
            }
          </div>
        )}
        
        {/* Question conditionnelle pour religiousPracticing */}
        {question.slot === 'religiousPracticing' && answers['religiousPracticing'] === 'yes' && (
          <div style={styles.conditionalQuestion}>
            {allQuestions
              .filter(q => q.slot === 'religiousType')
              .map(subQuestion => (
                <div key={subQuestion.slot} style={{ marginTop: '15px' }}>
                  <label style={styles.questionLabel}>
                    {subQuestion.text}
                    {subQuestion.required && <span style={styles.required}> *</span>}
                  </label>
                  {renderQuestionInput(subQuestion)}
                </div>
              ))
            }
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.spinner}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  const organizedQuestions = organizeQuestions(questions);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {/* Bouton de retour */}
        <button 
          onClick={handleBackClick} 
          style={styles.backButton}
          type="button"
          title="Back"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        
        {/* Bouton logout rouge */}
        <button 
          onClick={() => {
            logout();
            router.push('/auth');
          }} 
          style={styles.logoutButton}
          type="button"
          title="Logout"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
        
        <h1 style={styles.title}>
          {aiQuestion ? '🤖 One more thing...' : (isEditMode ? '✏️ Edit your profile' : '🍽️ Complete your profile')}
        </h1>
        
        {firstName && !aiQuestion && (
          <p style={styles.greeting}>
            {isEditMode 
              ? `${firstName}, you can edit your answers below 🎯` 
              : `Welcome ${firstName}! Help us get to know you better 🎯`
            }
          </p>
        )}

        {error && (
          <div style={styles.errorMessage}>
            {error}
          </div>
        )}
        
        {success && (
          <div style={styles.successMessage}>
            {success}
          </div>
        )}

        {/* Question IA après soumission */}
        {aiQuestion ? (
          <div style={styles.aiQuestionContainer}>
            <p style={styles.aiQuestionIntro}>
              To better personalize your experience, we'd like to know:
            </p>
            <div style={styles.questionBlock}>
              <label style={styles.questionLabel}>
                {aiQuestion.text}
              </label>
              {aiQuestion.type === 'single_choice' ? (
                <div style={styles.choicesContainer}>
                  {aiQuestion.choices.map((choice) => (
                    <button
                      key={choice}
                      type="button"
                      onClick={() => handleAnswerChange(aiQuestion.slot, choice)}
                      style={{
                        ...styles.choiceButton,
                        ...(answers[aiQuestion.slot] === choice ? styles.choiceButtonSelected : {})
                      }}
                    >
                      {choice}
                    </button>
                  ))}
                </div>
              ) : (
                <textarea
                  value={answers[aiQuestion.slot] || ''}
                  onChange={(e) => handleAnswerChange(aiQuestion.slot, e.target.value)}
                  style={{...styles.input, minHeight: '100px', resize: 'vertical'}}
                  placeholder={aiQuestion.placeholder || "Your answer..."}
                />
              )}
            </div>
            <div style={styles.aiButtonGroup}>
              <button 
                type="button"
                onClick={handleSkipAiQuestion}
                style={styles.skipButton}
                disabled={submitting}
              >
                Skip
              </button>
              <button 
                type="button"
                onClick={handleAiAnswerSubmit}
                style={styles.submitButton}
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={styles.form}>
          {Object.entries(organizedQuestions).map(([sectionName, sectionQuestions]) => (
            sectionQuestions.length > 0 && (
              <div key={sectionName} style={styles.section}>
                <h2 style={styles.sectionTitle}>{sectionName}</h2>
                {sectionQuestions.map((question, index) => (
                  shouldShowQuestion(question) && renderQuestionBlock(question, questions)
                ))}
              </div>
            )
          ))}

          <button 
            type="submit" 
            style={styles.submitButton}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Validate my profile ✨'}
          </button>
        </form>
        )}
      </div>
    </div>
  );
}

// Styles
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: '20px'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '40px',
    maxWidth: '800px',
    width: '100%',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    marginTop: '20px',
    marginBottom: '20px',
    position: 'relative'
  },
  backButton: {
    position: 'absolute',
    top: '20px',
    left: '20px',
    background: 'white',
    border: 'none',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    color: '#333'
  },
  logoutButton: {
    position: 'absolute',
    top: '20px',
    right: '20px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    color: '#e74c3c',
    padding: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s ease',
    borderRadius: '8px'
  },
  title: {
    textAlign: 'center',
    marginBottom: '10px',
    color: '#333',
    fontSize: '28px'
  },
  greeting: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#666',
    fontSize: '16px'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '35px'
  },
  section: {
    backgroundColor: '#fafafa',
    borderRadius: '10px',
    padding: '25px',
    border: '1px solid #e0e0e0'
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#4CAF50',
    marginBottom: '20px',
    paddingBottom: '10px',
    borderBottom: '2px solid #4CAF50'
  },
  questionBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '15px'
  },
  questionLabel: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#333',
    display: 'flex',
    alignItems: 'center',
    gap: '5px'
  },
  questionNumber: {
    color: '#4CAF50',
    fontWeight: 'bold',
    fontSize: '18px'
  },
  required: {
    color: '#f44336',
    fontSize: '18px'
  },
  choicesContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px'
  },
  choiceButton: {
    padding: '12px 15px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    backgroundColor: 'white',
    cursor: 'pointer',
    fontSize: '15px',
    transition: 'all 0.2s',
    textAlign: 'center',
    fontWeight: '500'
  },
  choiceButtonSelected: {
    borderColor: '#4CAF50',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32'
  },
  input: {
    padding: '12px 15px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    transition: 'border-color 0.2s',
    fontFamily: 'inherit'
  },
  submitButton: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '18px',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'background-color 0.2s'
  },
  backButton: {
    position: 'absolute',
    top: '20px',
    left: '20px',
    background: 'white',
    border: 'none',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    color: '#333'
  },
  errorMessage: {
    padding: '15px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center',
    fontWeight: '500'
  },
  successMessage: {
    padding: '15px',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
    borderRadius: '8px',
    marginBottom: '20px',
    textAlign: 'center',
    fontWeight: '500'
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #4CAF50',
    borderRadius: '50%',
    width: '40px',
    height: '40px',
    animation: 'spin 1s linear infinite',
    margin: '0 auto 20px'
  },
  tooltip: {
    position: 'absolute',
    bottom: '100%',
    left: '50%',
    transform: 'translateX(-50%)',
    marginBottom: '10px',
    padding: '12px 16px',
    backgroundColor: '#333',
    color: 'white',
    borderRadius: '8px',
    fontSize: '14px',
    whiteSpace: 'nowrap',
    zIndex: 1000,
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    maxWidth: '300px',
    whiteSpace: 'normal',
    textAlign: 'center',
    lineHeight: '1.4'
  },
  conditionalQuestion: {
    marginTop: '15px',
    paddingTop: '15px',
    paddingLeft: '20px',
    paddingRight: '10px',
    paddingBottom: '10px',
    borderLeft: '3px solid #4CAF50',
    backgroundColor: '#f0f9f0',
    borderRadius: '0 8px 8px 0'
  },
  aiQuestionContainer: {
    backgroundColor: '#f0f4ff',
    padding: '30px',
    borderRadius: '12px',
    border: '2px solid #4CAF50',
    marginTop: '20px'
  },
  aiQuestionIntro: {
    fontSize: '16px',
    color: '#555',
    marginBottom: '20px',
    textAlign: 'center',
    fontWeight: '500'
  },
  aiButtonGroup: {
    display: 'flex',
    gap: '15px',
    marginTop: '25px',
    justifyContent: 'center'
  },
  skipButton: {
    padding: '12px 30px',
    backgroundColor: 'transparent',
    color: '#666',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '600',
    transition: 'all 0.2s'
  }
};

