# 🚀 Guide Rapide - Système de Sessions

## Pour commencer en 3 étapes

### 1️⃣ Créer une session

```bash
curl -X POST "http://localhost:8000/api/session/create" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "mon_utilisateur"}'
```

**Réponse :**
```json
{
  "session_token": "abc-123-def-456",
  "user_id": "mon_utilisateur",
  "message": "Session créée..."
}
```

### 2️⃣ Utiliser le token dans vos requêtes

Ajoutez le header `X-Session-Token` à **toutes** vos requêtes :

```bash
# Analyser une assiette
curl -X POST "http://localhost:8000/api/analyze/plate" \
  -H "X-Session-Token: abc-123-def-456" \
  -F "file=@image.jpg"

# Analyser les nutriments
curl -X POST "http://localhost:8000/api/analyze/nutrients" \
  -H "X-Session-Token: abc-123-def-456" \
  -H "Content-Type: application/json" \
  -d '[{"name": "Poulet", "estimated_quantity": 150}]'

# Voir l'historique
curl -X GET "http://localhost:8000/api/analyze/history" \
  -H "X-Session-Token: abc-123-def-456"
```

### 3️⃣ C'est tout ! 🎉

Les analyses sont automatiquement liées à votre utilisateur.

---

## Intégration Frontend

### React Hook Exemple

```jsx
// hooks/useAuth.js
import { useState, useEffect } from 'react';

export function useAuth() {
  const [sessionToken, setSessionToken] = useState(null);

  useEffect(() => {
    // Récupérer ou créer une session
    const initSession = async () => {
      let token = localStorage.getItem('session_token');
      
      if (!token) {
        // Créer une nouvelle session
        const response = await fetch('/api/session/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        token = data.session_token;
        localStorage.setItem('session_token', token);
        localStorage.setItem('user_id', data.user_id);
      }
      
      setSessionToken(token);
    };

    initSession();
  }, []);

  return { sessionToken };
}

// Dans vos composants
function AnalyzeComponent() {
  const { sessionToken } = useAuth();

  const analyzeImage = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/analyze/plate', {
      method: 'POST',
      headers: {
        'X-Session-Token': sessionToken  // ← Le token ici !
      },
      body: formData
    });

    return response.json();
  };

  // ...
}
```

---

## Points clés à retenir

✅ **Toujours inclure** `X-Session-Token` dans les headers
✅ **Stocker** le token côté client (localStorage, cookie, etc.)
✅ **Durée de vie** : 24 heures
✅ **Erreur 401** : Créer une nouvelle session

---

## Tester localement

```bash
# 1. Démarrer le serveur
cd backend
python run.py

# 2. Tester le système de sessions
python tests/test_session_demo.py
```

---

## Documentation complète

- 📖 [SESSIONS_README.md](./SESSIONS_README.md) - Guide complet
- 🏗️ [SESSIONS_ARCHITECTURE.md](./SESSIONS_ARCHITECTURE.md) - Architecture détaillée
