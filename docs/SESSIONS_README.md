# 🔐 Système de Sessions Utilisateur

## Vue d'ensemble

Le système de sessions permet d'identifier et de tracker les utilisateurs à travers toutes leurs actions dans l'application (onboarding, analyses d'assiettes, analyses nutritionnelles).

## Architecture

### Collections MongoDB

1. **`user_sessions`** : Sessions utilisateur actives
   - `session_token` : UUID unique pour identifier la session
   - `user_id` : Identifiant de l'utilisateur
   - `created_at` : Date de création
   - `last_activity` : Dernière activité
   - `expires_at` : Date d'expiration (24h après création)
   - `metadata` : Statistiques (nombre d'analyses, onboarding complété, etc.)

2. **`plate_analyses`** : Historique des analyses d'assiettes
   - `user_id` : ID de l'utilisateur
   - `session_token` : Token de la session
   - `image_filename` : Nom du fichier image
   - `aliments` : Liste des aliments détectés
   - `analyzed_at` : Date de l'analyse

3. **`nutrient_analyses`** : Historique des analyses nutritionnelles
   - `user_id` : ID de l'utilisateur
   - `session_token` : Token de la session
   - `aliments` : Liste des aliments analysés
   - `nutrients` : Résultats détaillés
   - `nutrient_summary` : Résumé nutritionnel
   - `analyzed_at` : Date de l'analyse

## 📋 Utilisation

### 1. Créer une session

**Endpoint :** `POST /api/session/create`

```http
POST /api/session/create
Content-Type: application/json

{
  "user_id": "mon_utilisateur_123"  // Optionnel
}
```

**Réponse :**
```json
{
  "session_token": "abc-123-def-456",
  "user_id": "mon_utilisateur_123",
  "message": "Session créée avec succès. Utilisez 'X-Session-Token' dans les headers."
}
```

> ⚠️ **Important** : Conservez le `session_token` ! Vous devrez le passer dans toutes les requêtes suivantes.

### 2. Utiliser la session dans les requêtes

Pour toutes les routes protégées, ajoutez le header `X-Session-Token` :

```http
POST /api/analyze/plate
X-Session-Token: abc-123-def-456
Content-Type: multipart/form-data

[fichier image]
```

### 3. Routes disponibles

#### Routes de gestion de session

- **`POST /api/session/create`** : Créer une nouvelle session
- **`GET /api/session/info`** : Récupérer les infos de la session courante
- **`POST /api/session/validate`** : Vérifier qu'une session est valide
- **`GET /api/session/stats/{user_id}`** : Statistiques d'un utilisateur

#### Routes d'analyse (nécessitent une session)

- **`POST /api/analyze/plate`** : Analyser une assiette ✅ **Requiert session**
- **`POST /api/analyze/nutrients`** : Analyser les nutriments ✅ **Requiert session**
- **`GET /api/analyze/history`** : Historique des analyses d'assiettes ✅ **Requiert session**
- **`GET /api/analyze/nutrients/history`** : Historique nutritionnel ✅ **Requiert session**

## 🔄 Exemples d'utilisation

### Exemple complet avec curl

```bash
# 1. Créer une session
curl -X POST "http://localhost:8000/api/session/create" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice_123"}'

# Réponse: {"session_token": "abc-123", "user_id": "alice_123", ...}

# 2. Analyser une assiette
curl -X POST "http://localhost:8000/api/analyze/plate" \
  -H "X-Session-Token: abc-123" \
  -F "file=@mon_assiette.jpg"

# 3. Voir l'historique
curl -X GET "http://localhost:8000/api/analyze/history?limit=5" \
  -H "X-Session-Token: abc-123"
```

### Exemple avec Python (requests)

```python
import requests

# 1. Créer une session
response = requests.post(
    "http://localhost:8000/api/session/create",
    json={"user_id": "alice_123"}
)
session_data = response.json()
session_token = session_data["session_token"]

# Headers à utiliser pour toutes les requêtes
headers = {"X-Session-Token": session_token}

# 2. Analyser une assiette
with open("mon_assiette.jpg", "rb") as img:
    response = requests.post(
        "http://localhost:8000/api/analyze/plate",
        headers=headers,
        files={"file": img}
    )
    aliments = response.json()["aliments"]

# 3. Analyser les nutriments
response = requests.post(
    "http://localhost:8000/api/analyze/nutrients",
    headers=headers,
    json=aliments
)
nutrients = response.json()["nutrients"]

# 4. Voir l'historique
response = requests.get(
    "http://localhost:8000/api/analyze/history",
    headers=headers
)
historique = response.json()["analyses"]
```

### Exemple avec JavaScript (fetch)

```javascript
// 1. Créer une session
const createSession = async () => {
  const response = await fetch('http://localhost:8000/api/session/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'alice_123' })
  });
  const data = await response.json();
  return data.session_token;
};

// 2. Analyser une assiette
const analyzePlate = async (sessionToken, imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8000/api/analyze/plate', {
    method: 'POST',
    headers: { 'X-Session-Token': sessionToken },
    body: formData
  });
  return response.json();
};

// 3. Utilisation
const sessionToken = await createSession();
const result = await analyzePlate(sessionToken, myImageFile);
console.log('Aliments détectés:', result.aliments);
```

## 🔒 Sécurité et durée de vie

- **Durée de validité** : Les sessions expirent après **24 heures** d'inactivité
- **Vérification** : Chaque requête vérifie automatiquement la validité de la session
- **Mise à jour** : Le champ `last_activity` est mis à jour à chaque requête

## 📊 Suivi et statistiques

### Obtenir les statistiques d'un utilisateur

```http
GET /api/session/stats/alice_123

Response:
{
  "user_id": "alice_123",
  "total_sessions": 3,
  "total_analyses": 15,
  "onboarding_completed": true
}
```

### Consulter l'historique

```http
GET /api/analyze/history?limit=10
X-Session-Token: abc-123

Response:
{
  "user_id": "alice_123",
  "total": 5,
  "analyses": [
    {
      "user_id": "alice_123",
      "session_token": "abc-123",
      "aliments": [...],
      "analyzed_at": "2025-10-20T15:30:00"
    },
    ...
  ]
}
```

## 🔧 Intégration avec le frontend

### React / Next.js

```jsx
// hooks/useSession.js
import { useState, useEffect } from 'react';

export function useSession() {
  const [sessionToken, setSessionToken] = useState(null);

  useEffect(() => {
    // Récupérer le token depuis localStorage
    const token = localStorage.getItem('session_token');
    if (token) {
      setSessionToken(token);
    } else {
      // Créer une nouvelle session
      createNewSession();
    }
  }, []);

  const createNewSession = async (userId) => {
    const response = await fetch('/api/session/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
    const data = await response.json();
    localStorage.setItem('session_token', data.session_token);
    localStorage.setItem('user_id', data.user_id);
    setSessionToken(data.session_token);
  };

  return { sessionToken, createNewSession };
}

// Utilisation dans un composant
function AnalyzePlate() {
  const { sessionToken } = useSession();

  const handleAnalyze = async (file) => {
    if (!sessionToken) return;

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/analyze/plate', {
      method: 'POST',
      headers: { 'X-Session-Token': sessionToken },
      body: formData
    });

    const result = await response.json();
    // ... traiter le résultat
  };

  return (/* ... */);
}
```

## 🎯 Migration depuis l'ancien système

Si vous aviez des routes qui utilisaient directement `user_id` en query parameter, voici comment migrer :

### Avant (ancien système)
```http
POST /api/onboarding/start?user_id=alice_123
```

### Après (nouveau système)
```http
# 1. Créer une session
POST /api/session/create
{ "user_id": "alice_123" }

# 2. Utiliser le token
POST /api/onboarding/start
X-Session-Token: abc-123
```

## ❓ FAQ

**Q: Que se passe-t-il si ma session expire ?**
R: Vous recevrez une erreur 401 avec le message "Session expirée". Créez simplement une nouvelle session.

**Q: Puis-je avoir plusieurs sessions pour un même utilisateur ?**
R: Oui ! Un utilisateur peut avoir plusieurs sessions actives (navigateurs différents, appareils différents).

**Q: Les analyses sont-elles partagées entre les sessions ?**
R: Oui, toutes les analyses sont liées au `user_id`, donc elles sont accessibles depuis n'importe quelle session de cet utilisateur.

**Q: Comment supprimer une session ?**
R: Les sessions expirent automatiquement après 24h. Si besoin, nous pouvons ajouter une route `DELETE /api/session/logout`.
