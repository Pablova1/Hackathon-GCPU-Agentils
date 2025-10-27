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
  const [isEditMode, setIsEditMode] = useState(false);

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

      // Charger toutes les questions
      try {
        const questionsResponse = await fetch('http://localhost:8000/api/onboarding/questions');
        if (questionsResponse.ok) {
          const questionsData = await questionsResponse.json();
          
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
            const profileResponse = await fetch(`http://localhost:8000/api/profile/check?user_id=${storedUserId}`, {
              headers: {
                'Authorization': `Bearer ${sessionToken}`
              }
            });

            if (profileResponse.ok) {
              const profileData = await profileResponse.json();
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
            }
          } catch (err) {
            console.log('Impossible de charger les réponses existantes:', err);
          }
          
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

      if (response.ok) {
        setSuccess('Profil complété avec succès ! Redirection...');
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } else {
        setError(data.detail || 'Erreur lors de la soumission du profil');
        setSubmitting(false);
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
      setSubmitting(false);
    }
  };

  const renderQuestionInput = (question) => {
    const value = answers[question.slot] || '';

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
          <textarea
            value={value}
            onChange={(e) => handleAnswerChange(question.slot, e.target.value)}
            style={{...styles.input, minHeight: '80px', resize: 'vertical'}}
            placeholder={question.placeholder || "Votre réponse..."}
            required={question.required}
          />
        );
    }
  };

  // Organiser les questions par sections
  const organizeQuestions = (questions) => {
    const sections = {
      'Informations de base': ['birthDate', 'gender', 'heightCm', 'weightKg', 'bodyType'],
      'Nutrition': ['dietType', 'allergies', 'intolerances', 'foodLikes', 'foodDislikes', 'foodPreferences'],
      'Santé': ['treatments', 'medicalHistoryPersonal', 'medicalHistoryFamily', 'birthControl', 'birthControlName'],
      'Objectifs': ['goalMuscleGain', 'goalWeightLoss', 'goalPerformance', 'goalMaintainShape', 'goalDetail'],
      'Restrictions religieuses': ['religiousPracticing', 'religiousType'],
      'Activité et mode de vie': ['activityLevel', 'sports', 'occupation', 'additionalNotes']
    };

    const organized = {};
    Object.keys(sections).forEach(sectionName => {
      organized[sectionName] = questions.filter(q => sections[sectionName].includes(q.slot));
    });

    return organized;
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

  const organizedQuestions = organizeQuestions(questions);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        {isEditMode && (
          <button 
            onClick={() => router.push('/')} 
            style={styles.backButton}
            type="button"
          >
            ← Retour
          </button>
        )}
        
        <h1 style={styles.title}>
          {isEditMode ? '✏️ Modifie ton profil' : '🍽️ Complète ton profil'}
        </h1>
        
        {firstName && (
          <p style={styles.greeting}>
            {isEditMode 
              ? `${firstName}, tu peux modifier tes réponses ci-dessous 🎯` 
              : `Bienvenue ${firstName} ! Aide-nous à mieux te connaître 🎯`
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

        <form onSubmit={handleSubmit} style={styles.form}>
          {Object.entries(organizedQuestions).map(([sectionName, sectionQuestions]) => (
            sectionQuestions.length > 0 && (
              <div key={sectionName} style={styles.section}>
                <h2 style={styles.sectionTitle}>{sectionName}</h2>
                {sectionQuestions.map((question, index) => (
                  <div key={question.slot} style={styles.questionBlock}>
                    <label style={styles.questionLabel}>
                      {question.text}
                      {question.required && <span style={styles.required}> *</span>}
                    </label>
                    {renderQuestionInput(question)}
                  </div>
                ))}
              </div>
            )
          ))}

          <button 
            type="submit" 
            style={styles.submitButton}
            disabled={submitting}
          >
            {submitting ? 'Envoi en cours...' : 'Valider mon profil ✨'}
          </button>
        </form>
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
    padding: '10px 20px',
    backgroundColor: '#f5f5f5',
    color: '#666',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    fontSize: '14px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '5px'
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
    marginBottom: '20px',
    padding: '10px 20px',
    backgroundColor: 'transparent',
    color: '#4CAF50',
    border: '2px solid #4CAF50',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '600',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '5px'
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
