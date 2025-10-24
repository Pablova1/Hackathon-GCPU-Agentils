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
    transition: 'border-color 0.2s'
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
