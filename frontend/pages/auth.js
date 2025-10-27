import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Image from 'next/image';
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
    // Si le paramètre ?logout=true est présent, déconnecter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('logout') === 'true') {
      localStorage.clear();
      window.history.replaceState({}, '', '/auth');
      return;
    }
    
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

        setSuccess('Login successful! Redirecting...');
        
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
          setError('Login error');
        }
      }
    } catch (err) {
      setError('Server connection error. Please check that the API is running.');
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
      setError('Passwords do not match');
      return;
    }

    if (registerData.password.length < 6) {
      setError('Password must be at least 6 characters long');
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

        setSuccess('Registration successful! Redirecting to onboarding...');
        
        // Rediriger vers l'onboarding après l'inscription
        setTimeout(() => {
          router.push('/onboarding-new');
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
          setError('Registration error');
        }
      }
    } catch (err) {
      setError('Server connection error. Please check that the API is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container} data-tab={activeTab}>
      {activeTab === 'register' && (
        <div className={styles.logoContainer}>
          <Image 
            src="/logo-4.png" 
            alt="MY PLATE Logo" 
            width={200}
            height={200}
            priority
            style={{ objectFit: 'contain' }}
          />
        </div>
      )}
      <div className={styles.card} data-tab={activeTab}>
        <div className={styles.header} data-tab={activeTab}>
          <h1>MY PLATE</h1>
          <p>{activeTab === 'register' ? 'Create your account' : 'Welcome back!'}</p>
        </div>

        <div className={styles.tabs} data-tab={activeTab}>
          <button 
            className={`${styles.tab} ${activeTab === 'login' ? styles.active : ''}`}
            onClick={() => setActiveTab('login')}
          >
            Login
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'register' ? styles.active : ''}`}
            onClick={() => setActiveTab('register')}
          >
            Sign Up
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
              <p>Processing...</p>
            </div>
          )}

          {/* Formulaire de connexion */}
          {activeTab === 'login' && !loading && (
            <form onSubmit={handleLogin} className={styles.form}>
              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="loginEmail">Email</label>
                <input
                  type="email"
                  id="loginEmail"
                  placeholder="your.email@example.com"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="loginPassword">Password</label>
                <input
                  type="password"
                  id="loginPassword"
                  placeholder="Your password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className={styles.submitButton} data-tab={activeTab}>
                Log In
              </button>
            </form>
          )}

          {/* Formulaire d'inscription */}
          {activeTab === 'register' && !loading && (
            <form onSubmit={handleRegister} className={styles.form}>
              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="registerFirstName">First Name</label>
                <input
                  type="text"
                  id="registerFirstName"
                  placeholder="Your first name"
                  minLength="1"
                  maxLength="50"
                  value={registerData.first_name}
                  onChange={(e) => setRegisterData({ ...registerData, first_name: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="registerLastName">Last Name</label>
                <input
                  type="text"
                  id="registerLastName"
                  placeholder="Your last name"
                  minLength="1"
                  maxLength="50"
                  value={registerData.last_name}
                  onChange={(e) => setRegisterData({ ...registerData, last_name: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="registerEmail">Email</label>
                <input
                  type="email"
                  id="registerEmail"
                  placeholder="your.email@example.com"
                  value={registerData.email}
                  onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="registerPassword">Password</label>
                <input
                  type="password"
                  id="registerPassword"
                  placeholder="Minimum 6 characters"
                  minLength="6"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                  required
                />
              </div>

              <div className={styles.formGroup} data-tab={activeTab}>
                <label htmlFor="registerPasswordConfirm">Confirm Password</label>
                <input
                  type="password"
                  id="registerPasswordConfirm"
                  placeholder="Repeat your password"
                  value={registerData.passwordConfirm}
                  onChange={(e) => setRegisterData({ ...registerData, passwordConfirm: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className={styles.submitButton} data-tab={activeTab}>
                Sign Up
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
