import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Onboarding() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [userId, setUserId] = useState(null);
  const [firstName, setFirstName] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [aiQuestions, setAiQuestions] = useState([]);
  const [aiAnswers, setAiAnswers] = useState({});
  const [showAiQuestions, setShowAiQuestions] = useState(false);
  const [aiSubmitting, setAiSubmitting] = useState(false);

  // Vérifier l'authentification et charger les questions
  useEffect(() => {
    const checkAuthAndLoadQuestions = async () => {
      const sessionToken = localStorage.getItem('session_token');
      const storedUserId = localStorage.getItem('user_id');
      const storedFirstName = localStorage.getItem('first_name');

      // Si pas connecté, rediriger vers la page d'auth
      if (!sessionToken || !storedUserId) {
        router.push('/auth');
        return;
      }

      setUserId(storedUserId);
      setFirstName(storedFirstName || '');

      // Vérifier si le profil est déjà complété
      try {
        const response = await fetch(`http://localhost:8000/api/profile/check?user_id=${storedUserId}`, {
          headers: {
            'Authorization': `Bearer ${sessionToken}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          if (data.profile_completed) {
            // Profil déjà complété, rediriger vers la page principale
            router.push('/');
            return;
          }
        }
      } catch (err) {
        console.log('Erreur lors de la vérification du profil:', err);
      }

      // Charger toutes les questions
      try {
        const questionsResponse = await fetch('http://localhost:8000/api/onboarding/questions');
        if (questionsResponse.ok) {
          const questionsData = await questionsResponse.json();
          setQuestions(questionsData.questions);
          
          // Initialiser les réponses vides
          const initialAnswers = {};
          questionsData.questions.forEach(q => {
            initialAnswers[q.slot] = '';
          });
          setAnswers(initialAnswers);
          
          setLoading(false);
        } else {
          setError('Erreur lors du chargement des questions');
          setLoading(false);
        }
      } catch (err) {
        setError('Erreur de connexion au serveur');
        setLoading(false);
      }
    };

    checkAuthAndLoadQuestions();
  }, [router]);

  const handleAnswerChange = (slot, value) => {
    setAnswers(prev => ({
      ...prev,
      [slot]: value
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
      setError('Veuillez répondre à toutes les questions obligatoires');
      setSubmitting(false);
      return;
    }

    // Convertir les réponses au bon type
    const processedAnswers = {};
    questions.forEach(q => {
      let value = answers[q.slot];
      
      if (q.type === 'number') {
        value = parseFloat(value);
        if (isNaN(value)) {
          setError(`Valeur invalide pour: ${q.text}`);
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
      const response = await fetch('http://localhost:8000/api/onboarding/submit-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          answers: processedAnswers
        })
      });

      const data = await response.json();

      console.log('Réponse du backend:', data);

      if (response.ok) {
        setSessionId(data.session_id);
        
        // Vérifier s'il y a une question IA
        if (data.ai_question) {
          console.log('Question IA reçue:', data.ai_question);
          setAiQuestions([data.ai_question]);
          setAiAnswers({ [data.ai_question.slot]: '' });
          setSuccess('Profil complété ! Quelques questions supplémentaires pour mieux te connaître...');
          setShowAiQuestions(true);
          setSubmitting(false);
        } else {
          console.log('Pas de question IA, redirection...');
          // Pas de questions IA, rediriger directement
          setSuccess('Profil complété avec succès ! Redirection...');
          setTimeout(() => {
            router.push('/');
          }, 2000);
        }
      } else {
        setError(data.detail || 'Erreur lors de la soumission du profil');
        setSubmitting(false);
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      setSubmitting(false);
    }
  };

  const handleAiAnswerChange = (slot, value) => {
    setAiAnswers(prev => ({
      ...prev,
      [slot]: value
    }));
  };

  const handleAiSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setAiSubmitting(true);

    const currentQuestion = aiQuestions[0];
    const answer = aiAnswers[currentQuestion.slot];

    if (!answer || answer === '') {
      setError('Veuillez répondre à la question');
      setAiSubmitting(false);
      return;
    }

    try {
      // Soumettre la réponse IA
      const response = await fetch('http://localhost:8000/api/onboarding/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          slot: currentQuestion.slot,
          value: answer
        })
      });

      const data = await response.json();

      if (response.ok) {
        if (data.finished) {
          // Toutes les questions sont terminées
          setSuccess('Profil complété avec succès ! Redirection...');
          setTimeout(() => {
            router.push('/');
          }, 2000);
        } else if (data.next_question) {
          // Il y a une autre question IA
          setAiQuestions([data.next_question]);
          setAiAnswers({ [data.next_question.slot]: '' });
          setAiSubmitting(false);
        } else {
          // Pas de prochaine question, terminer
          setSuccess('Profil complété avec succès ! Redirection...');
          setTimeout(() => {
            router.push('/');
          }, 2000);
        }
      } else {
        setError(data.detail || 'Erreur lors de la soumission');
        setAiSubmitting(false);
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      setAiSubmitting(false);
    }
  };

  const skipAiQuestions = () => {
    setSuccess('Profil complété avec succès ! Redirection...');
    setTimeout(() => {
      router.push('/');
    }, 2000);
  };

  // Descriptions des morphologies
  const morphologyDescriptions = {
    'ectomorphic': {
      emoji: '🏃',
      description: 'Corps naturellement mince avec un métabolisme rapide. Difficulté à prendre du poids et de la masse musculaire.',
      characteristics: ['Métabolisme rapide', 'Silhouette élancée', 'Peu de masse grasse']
    },
    'mesomorphic': {
      emoji: '💪',
      description: 'Corps athlétique et musclé naturellement. Gains musculaires et perte de graisse relativement faciles.',
      characteristics: ['Développement musculaire facile', 'Corps athlétique', 'Métabolisme équilibré']
    },
    'endomorphic': {
      emoji: '🏋️',
      description: 'Corps qui stocke facilement la graisse. Métabolisme plus lent mais bon potentiel de force.',
      characteristics: ['Facilité à prendre du poids', 'Métabolisme lent', 'Bonne force naturelle']
    },
    'unknown': {
      emoji: '❓',
      description: 'Tu ne connais pas ton type de morphologie ? Pas de problème, nous t\'aiderons à l\'identifier !',
      characteristics: ['Évaluation personnalisée', 'Conseils adaptés', 'Suivi progressif']
    }
  };

  const renderQuestionInput = (question) => {
    const value = answers[question.slot] || '';
    const isMorphologyQuestion = question.slot === 'bodyType';
    const isDietQuestion = question.slot === 'dietType';

    // Gérer la sélection multiple pour dietType
    const handleMultipleChoice = (choice) => {
      const currentValues = value ? value.split(',').map(v => v.trim()) : [];
      let newValues;
      
      if (currentValues.includes(choice)) {
        // Désélectionner
        newValues = currentValues.filter(v => v !== choice);
      } else {
        // Sélectionner
        newValues = [...currentValues, choice];
      }
      
      handleAnswerChange(question.slot, newValues.join(','));
    };

    const isChoiceSelected = (choice) => {
      if (!isDietQuestion) return value === choice;
      const currentValues = value ? value.split(',').map(v => v.trim()) : [];
      return currentValues.includes(choice);
    };

    switch (question.type) {
      case 'single_choice':
        return (
          <div>
            {isDietQuestion && (
              <p style={styles.multiSelectHint}>💡 Tu peux sélectionner plusieurs régimes</p>
            )}
            <div style={styles.choicesContainer}>
              {question.choices.map((choice) => (
                <button
                  key={choice}
                  type="button"
                  onClick={(e) => {
                    if (isDietQuestion) {
                      handleMultipleChoice(choice);
                    } else {
                      handleAnswerChange(question.slot, choice);
                    }
                    e.target.blur(); // Retire le focus après le clic
                  }}
                  style={{
                    ...styles.choiceButton,
                    ...(isChoiceSelected(choice) ? styles.choiceButtonSelected : {})
                  }}
                >
                  {isMorphologyQuestion && morphologyDescriptions[choice] && (
                    <span style={styles.choiceEmoji}>{morphologyDescriptions[choice].emoji} </span>
                  )}
                  {choice}
                </button>
              ))}
            </div>
            
            {isMorphologyQuestion && value && morphologyDescriptions[value] && (
              <div style={styles.morphologyInfo}>
                <div style={styles.morphologyHeader}>
                  <span style={styles.morphologyEmoji}>{morphologyDescriptions[value].emoji}</span>
                  <strong>{value}</strong>
                </div>
                <p style={styles.morphologyDescription}>
                  {morphologyDescriptions[value].description}
                </p>
                <ul style={styles.characteristicsList}>
                  {morphologyDescriptions[value].characteristics.map((char, idx) => (
                    <li key={idx} style={styles.characteristicItem}>✓ {char}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'number':
        return (
          <input
            type="number"
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={styles.input}
            placeholder={question.placeholder || "Entrez un nombre"}
            step="any"
            required={question.required}
          />
        );

      case 'date':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={styles.input}
            placeholder={question.placeholder || "JJ/MM/AAAA"}
            required={question.required}
          />
        );

      case 'text':
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={styles.input}
            placeholder={question.placeholder || "Votre réponse..."}
            required={question.required}
          />
        );
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={styles.spinner}></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <style jsx>{`
        button:focus {
          outline: none !important;
          box-shadow: none !important;
        }
        button:active {
          outline: none !important;
          box-shadow: none !important;
        }
      `}</style>
      
      <div style={styles.card}>
        <h1 style={styles.title}>🍽️ Complète ton profil</h1>
        
        {firstName && (
          <p style={styles.greeting}>Bienvenue {firstName} ! Aide-nous à mieux te connaître 🎯</p>
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

        {!showAiQuestions ? (
          <form onSubmit={handleSubmit} style={styles.form}>
            {questions.map((question, index) => (
              <div key={question.slot} style={styles.questionBlock}>
                <label style={styles.questionLabel}>
                  <span style={styles.questionNumber}>{index + 1}.</span>
                  {question.text}
                  {question.required && <span style={styles.required}> *</span>}
                </label>
                {renderQuestionInput(question)}
              </div>
            ))}

            <button 
              type="submit" 
              style={styles.submitButton}
              disabled={submitting}
            >
              {submitting ? 'Envoi en cours...' : 'Valider mon profil ✨'}
            </button>
          </form>
        ) : (
          <div style={styles.aiSection}>
            <div style={styles.aiHeader}>
              <h2 style={styles.aiTitle}>🤖 Questions personnalisées par IA</h2>
              <p style={styles.aiSubtitle}>
                Notre IA a généré quelques questions pour mieux comprendre tes besoins
              </p>
            </div>

            {aiQuestions.length > 0 && (
              <form onSubmit={handleAiSubmit} style={styles.form}>
                {aiQuestions.map((question, index) => (
                  <div key={question.slot} style={styles.aiQuestionBlock}>
                    <label style={styles.questionLabel}>
                      <span style={styles.aiQuestionIcon}>🤖</span>
                      {question.text}
                    </label>
                    <textarea
                      value={aiAnswers[question.slot] || ''}
                      onChange={(e) => handleAiAnswerChange(question.slot, e.target.value)}
                      style={styles.textarea}
                      placeholder="Partage-nous tes préférences..."
                      rows={4}
                    />
                  </div>
                ))}

                <div style={styles.aiButtonsContainer}>
                  <button 
                    type="submit" 
                    style={styles.submitButton}
                    disabled={aiSubmitting}
                  >
                    {aiSubmitting ? 'Envoi en cours...' : 'Répondre 💬'}
                  </button>
                  
                  <button 
                    type="button"
                    onClick={skipAiQuestions}
                    style={styles.skipButton}
                  >
                    Passer cette étape →
                  </button>
                </div>
              </form>
            )}
          </div>
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
    maxWidth: '700px',
    width: '100%',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    marginTop: '20px',
    marginBottom: '20px'
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
    gap: '25px'
  },
  questionBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
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
    color: '#555',
    cursor: 'pointer',
    fontSize: '15px',
    transition: 'all 0.2s',
    textAlign: 'center',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    outline: 'none'
  },
  choiceEmoji: {
    fontSize: '20px',
    marginRight: '5px'
  },
  choiceButtonSelected: {
    borderColor: '#4CAF50',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32'
  },
  morphologyInfo: {
    marginTop: '15px',
    padding: '20px',
    backgroundColor: '#f0f7ff',
    borderRadius: '10px',
    border: '2px solid #2196F3',
    animation: 'fadeIn 0.3s ease-in'
  },
  morphologyHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '10px',
    fontSize: '18px',
    color: '#1976D2'
  },
  morphologyEmoji: {
    fontSize: '24px'
  },
  morphologyDescription: {
    margin: '10px 0',
    color: '#555',
    fontSize: '15px',
    lineHeight: '1.5'
  },
  characteristicsList: {
    listStyle: 'none',
    padding: '0',
    margin: '10px 0 0 0'
  },
  characteristicItem: {
    padding: '5px 0',
    color: '#2e7d32',
    fontSize: '14px',
    fontWeight: '500'
  },
  input: {
    padding: '12px 15px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    transition: 'border-color 0.2s'
  },
  textarea: {
    padding: '12px 15px',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    transition: 'border-color 0.2s',
    fontFamily: 'inherit',
    resize: 'vertical',
    minHeight: '100px'
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
  skipButton: {
    marginTop: '10px',
    padding: '12px',
    backgroundColor: 'transparent',
    color: '#666',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s'
  },
  aiSection: {
    marginTop: '20px'
  },
  aiHeader: {
    textAlign: 'center',
    marginBottom: '30px',
    padding: '20px',
    backgroundColor: '#f0f4ff',
    borderRadius: '10px',
    border: '2px solid #2196F3'
  },
  aiTitle: {
    color: '#1976D2',
    fontSize: '22px',
    marginBottom: '10px'
  },
  aiSubtitle: {
    color: '#666',
    fontSize: '15px',
    margin: '0'
  },
  aiQuestionBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    padding: '20px',
    backgroundColor: '#fafafa',
    borderRadius: '10px',
    border: '2px solid #e0e0e0'
  },
  aiQuestionIcon: {
    fontSize: '20px',
    marginRight: '8px'
  },
  aiButtonsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  multiSelectHint: {
    fontSize: '14px',
    color: '#2196F3',
    fontStyle: 'italic',
    marginBottom: '10px',
    textAlign: 'center',
    fontWeight: '500'
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
  }
};
