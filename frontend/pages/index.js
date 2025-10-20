import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [username, setUsername] = useState('');

  // Vérifier l'authentification au chargement
  useEffect(() => {
    const token = localStorage.getItem('session_token');
    const user = localStorage.getItem('username');
    
    if (!token) {
      // Pas de session, rediriger vers la page d'authentification
      router.push('/auth');
    } else {
      setSessionToken(token);
      setUsername(user || 'Utilisateur');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    router.push('/auth');
  };

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please upload an image.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/analyze/plate', {
        method: 'POST',
        headers: {
          'X-Session-Token': sessionToken  // Ajouter le token d'authentification
        },
        body: formData,
      });

      if (!res.ok) {
        if (res.status === 401) {
          // Session expirée, rediriger vers login
          handleLogout();
          return;
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      setResponse(null);
    }
  };

  const handleAlimentChange = (index, field, value) => {
    const updatedAliments = [...response.aliments];
    updatedAliments[index][field] = value;
    setResponse({ ...response, aliments: updatedAliments });
  };

  const handleAddAliment = () => {
    const newAliment = { nom: '', quantite_estimee: 0 };
    setResponse({ ...response, aliments: [...response.aliments, newAliment] });
  };

  const handleDeleteAliment = (index) => {
    const updatedAliments = response.aliments.filter((_, i) => i !== index);
    setResponse({ ...response, aliments: updatedAliments });
  };

  const handleValidateAliments = async () => {
    if (!response || !response.aliments) {
      setError('No aliments to validate.');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/analyze/nutrients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': sessionToken  // Ajouter le token d'authentification
        },
        body: JSON.stringify(response.aliments), // Send the list of aliments directly
      });

      if (!res.ok) {
        if (res.status === 401) {
          // Session expirée, rediriger vers login
          handleLogout();
          return;
        }
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Nutrient analysis result:', data);
      alert('Nutrient analysis completed! Check the console for details.');
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // Ne pas afficher la page si pas de session
  if (!sessionToken) {
    return <div style={{ padding: '20px' }}>Chargement...</div>;
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Food Analyzer</h1>
        <div>
          <span style={{ marginRight: '15px' }}>Bonjour, {username}!</span>
          <button onClick={handleLogout} style={{ 
            padding: '8px 16px',
            background: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Déconnexion
          </button>
        </div>
      </div>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="file">Upload an image of your plate:</label>
          <input type="file" id="file" accept="image/*" onChange={handleFileChange} />
        </div>
        <button type="submit">Analyze</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {response && (
        <div>
          <h2>Analysis Result</h2>
          <p>{response.message}</p>
          <ul>
            {response.aliments.map((aliment, index) => (
              <li key={index}>
                <input
                  type="text"
                  value={aliment.name}
                  onChange={(e) => handleAlimentChange(index, 'name', e.target.value)}
                  placeholder="Nom de l'aliment"
                />
                <input
                  type="number"
                  value={aliment.estimated_quantity}
                  onChange={(e) => handleAlimentChange(index, 'estimated_quantity', parseInt(e.target.value, 10))}
                  placeholder="Quantité"
                />
                <button onClick={() => handleDeleteAliment(index)}>Delete</button>
              </li>
            ))}
          </ul>
          <button onClick={handleAddAliment}>Add Aliment</button>
          <button onClick={handleValidateAliments}>Validate Aliments</button>
        </div>
      )}
    </div>
  );
}