import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/Auth.module.css';

export default function Auth() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Formulaire de connexion
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  
  // Formulaire d'inscription
  const [registerData, setRegisterData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    passwordConfirm: ''
  });

  // Vérifier si déjà connecté au chargement
  useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      // Déjà connecté, rediriger vers l'app
      router.push('/');
    }
  }, [router]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginData.email,
          password: loginData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Sauvegarder dans localStorage
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('first_name', data.first_name);
        localStorage.setItem('last_name', data.last_name);
        localStorage.setItem('email', data.email);

        setSuccess('Connexion réussie ! Redirection...');
        
        // Rediriger vers la page principale après 1 seconde
        setTimeout(() => {
          router.push('/');
        }, 1000);
      } else {
        // Gérer les erreurs de validation (422) et les erreurs métier (400)
        if (Array.isArray(data.detail)) {
          // Erreur de validation Pydantic (422)
          const errorMessages = data.detail.map(err => err.msg).join(', ');
          setError(errorMessages);
        } else if (typeof data.detail === 'string') {
          // Erreur métier (400)
          setError(data.detail);
        } else {
          setError('Erreur de connexion');
        }
      }
    } catch (err) {
      setError('Erreur de connexion au serveur. Vérifiez que l\'API est démarrée.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (registerData.password !== registerData.passwordConfirm) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (registerData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: registerData.first_name,
          last_name: registerData.last_name,
          email: registerData.email,
          password: registerData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Sauvegarder dans localStorage
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('first_name', data.first_name);
        localStorage.setItem('last_name', data.last_name);
        localStorage.setItem('email', data.email);

        setSuccess('Inscription réussie ! Redirection...');
        
        // Rediriger vers la page principale après 1 seconde
        setTimeout(() => {
          router.push('/');
        }, 1000);
      } else {
        // Gérer les erreurs de validation (422) et les erreurs métier (400)
        if (Array.isArray(data.detail)) {
          // Erreur de validation Pydantic (422)
          const errorMessages = data.detail.map(err => err.msg).join(', ');
          setError(errorMessages);
        } else if (typeof data.detail === 'string') {
          // Erreur métier (400)
          setError(data.detail);
        } else {
          setError('Erreur lors de l\'inscription');
        }
      }
    } catch (err) {
      setError('Erreur de connexion au serveur. Vérifiez que l\'API est démarrée.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1>🍽️ Nutrition App</h1>
          <p>Commencez votre parcours santé</p>
        </div>

        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${activeTab === 'login' ? styles.active : ''}`}
            onClick={() => setActiveTab('login')}
          >
            Connexion
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'register' ? styles.active : ''}`}
            onClick={() => setActiveTab('register')}
          >
            Inscription
          </button>
        </div>

        <div className={styles.formContainer}>
          {/* Messages */}
          {success && (
            <div className={styles.successMessage}>
              {success}
            </div>
          )}
          
          {error && (
            <div className={styles.errorMessage}>
              {error}
            </div>
          )}

          {loading && (
            <div className={styles.loading}>
              <div className={styles.spinner}></div>
              <p>Traitement en cours...</p>
            </div>
          )}

          {/* Formulaire de connexion */}
          {activeTab === 'login' && !loading && (
            <form onSubmit={handleLogin} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="loginEmail">Email</label>
                <input
                  type="email"
                  id="loginEmail"
                  placeholder="votre.email@example.com"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="loginPassword">Mot de passe</label>
                <input
                  type="password"
                  id="loginPassword"
                  placeholder="Votre mot de passe"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className={styles.submitButton}>
                Se connecter
              </button>
            </form>
          )}

          {/* Formulaire d'inscription */}
          {activeTab === 'register' && !loading && (
            <form onSubmit={handleRegister} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="registerFirstName">Prénom</label>
                <input
                  type="text"
                  id="registerFirstName"
                  placeholder="Votre prénom"
                  minLength="1"
                  maxLength="50"
                  value={registerData.first_name}
                  onChange={(e) => setRegisterData({ ...registerData, first_name: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="registerLastName">Nom</label>
                <input
                  type="text"
                  id="registerLastName"
                  placeholder="Votre nom de famille"
                  minLength="1"
                  maxLength="50"
                  value={registerData.last_name}
                  onChange={(e) => setRegisterData({ ...registerData, last_name: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="registerEmail">Email</label>
                <input
                  type="email"
                  id="registerEmail"
                  placeholder="votre.email@example.com"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="registerPassword">Mot de passe</label>
                <input
                  type="password"
                  id="registerPassword"
                  placeholder="Minimum 6 caractères"
                  minLength="6"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup}>
                <label htmlFor="registerPasswordConfirm">Confirmer le mot de passe</label>
                <input
                  type="password"
                  id="registerPasswordConfirm"
                  placeholder="Répétez votre mot de passe"
                  value={registerData.passwordConfirm}
                  onChange={(e) => setRegisterData({ ...registerData, passwordConfirm: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className={styles.submitButton}>
                S'inscrire
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
