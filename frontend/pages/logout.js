import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Logout() {
  const router = useRouter();

  useEffect(() => {
    // Effacer toutes les données de session
    localStorage.clear();
    
    // Rediriger vers la page d'authentification
    setTimeout(() => {
      router.push('/auth');
    }, 500);
  }, [router]);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>👋 Déconnexion...</h1>
        <p>Vous allez être redirigé vers la page de connexion.</p>
      </div>
    </div>
  );
}

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
    maxWidth: '500px',
    width: '100%',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    textAlign: 'center'
  },
  title: {
    marginBottom: '20px',
    color: '#333',
    fontSize: '24px'
  }
};
