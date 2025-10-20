# 🔐 Système d'Authentification

## Vue d'ensemble

Le système d'authentification permet aux utilisateurs de créer un compte et de se connecter. Chaque connexion crée automatiquement une session pour tracker les actions de l'utilisateur.

## Architecture

### Collection MongoDB: `user`

**⚠️ Important** : La collection s'appelle **`user`** (singulier), pas `users`.

```json
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123def456",
  "email": "alice@example.com",
  "username": "Alice",
  "password_hash": "sha256_hash_here",
  "created_at": ISODate("2025-10-20T10:00:00"),
  "last_login": ISODate("2025-10-20T15:30:00"),
  "profile_completed": false,
  "profile": null,
  "medical": null,
  "nutrition": null,
  "goals": null
}
```

> **Note** : Les champs `profile`, `medical`, etc. sont ajoutés lors de l'onboarding.  
> Voir [docs/USER_SCHEMA.md](docs/USER_SCHEMA.md) pour le schéma complet.

## Routes API

### 1. Inscription

**POST** `/api/auth/register`

```json
{
  "email": "alice@example.com",
  "password": "monMotDePasse123",
  "username": "Alice"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Inscription réussie ! Vous êtes maintenant connecté.",
  "session_token": "abc-123-def-456",
  "user_id": "user_abc123",
  "username": "Alice",
  "email": "alice@example.com"
}
```

### 2. Connexion

**POST** `/api/auth/login`

```json
{
  "email": "alice@example.com",
  "password": "monMotDePasse123"
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Connexion réussie !",
  "session_token": "abc-123-def-456",
  "user_id": "user_abc123",
  "username": "Alice",
  "email": "alice@example.com"
}
```

### 3. Vérifier disponibilité email

**GET** `/api/auth/check-email/{email}`

**Réponse:**
```json
{
  "email": "alice@example.com",
  "available": false
}
```

### 4. Vérifier disponibilité username

**GET** `/api/auth/check-username/{username}`

**Réponse:**
```json
{
  "username": "Alice",
  "available": false
}
```

## 🧪 Test avec la page HTML

### 1. Démarrer le serveur

```bash
cd backend
python run.py
```

### 2. Ouvrir la page de test

Ouvrez le fichier dans votre navigateur:
```
backend/test_auth.html
```

Ou utilisez un serveur local:
```bash
# Avec Python
python -m http.server 8080

# Puis ouvrez: http://localhost:8080/test_auth.html
```

### 3. Utiliser la page

1. **Inscription** : Créez un nouveau compte
   - Entrez votre nom d'utilisateur
   - Entrez votre email
   - Choisissez un mot de passe (min 6 caractères)
   - Confirmez le mot de passe

2. **Connexion** : Connectez-vous avec un compte existant
   - Entrez votre email
   - Entrez votre mot de passe

3. **Session automatique** : Après connexion/inscription
   - Le `session_token` est automatiquement sauvegardé dans localStorage
   - Vous pouvez maintenant utiliser ce token pour toutes les requêtes API

## 🔄 Flux complet

```
1. Utilisateur s'inscrit
   └─> Création dans collection "users"
   └─> Création automatique d'une session
   └─> Retour du session_token

2. Frontend sauvegarde le token
   └─> localStorage.setItem('session_token', token)

3. Toutes les requêtes suivantes incluent le token
   └─> Header: X-Session-Token: abc-123...

4. Backend identifie automatiquement l'utilisateur
   └─> via Depends(get_current_session)
```

## 💻 Exemples de code

### Avec JavaScript (fetch)

```javascript
// Inscription
const register = async () => {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'alice@example.com',
      password: 'motdepasse123',
      username: 'Alice'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Sauvegarder le token
    localStorage.setItem('session_token', data.session_token);
    console.log('Inscrit avec succès!', data);
  }
};

// Connexion
const login = async () => {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'alice@example.com',
      password: 'motdepasse123'
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    localStorage.setItem('session_token', data.session_token);
    console.log('Connecté avec succès!', data);
  }
};

// Utiliser le token pour une requête
const analyzePlate = async (imageFile) => {
  const token = localStorage.getItem('session_token');
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const response = await fetch('http://localhost:8000/api/analyze/plate', {
    method: 'POST',
    headers: {
      'X-Session-Token': token
    },
    body: formData
  });
  
  return response.json();
};
```

### Avec Python (requests)

```python
import requests

# Inscription
def register(email, password, username):
    response = requests.post(
        'http://localhost:8000/api/auth/register',
        json={
            'email': email,
            'password': password,
            'username': username
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['session_token']
    else:
        raise Exception(response.json()['detail'])

# Connexion
def login(email, password):
    response = requests.post(
        'http://localhost:8000/api/auth/login',
        json={
            'email': email,
            'password': password
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data['session_token']
    else:
        raise Exception(response.json()['detail'])

# Utilisation
token = register('alice@example.com', 'motdepasse123', 'Alice')
# ou
token = login('alice@example.com', 'motdepasse123')

# Utiliser le token
headers = {'X-Session-Token': token}
response = requests.get(
    'http://localhost:8000/api/analyze/history',
    headers=headers
)
```

## 🔒 Sécurité

### Actuellement implémenté

✅ Hash SHA256 des mots de passe (avec salt)
✅ Validation des emails (format)
✅ Longueur minimale des mots de passe (6 caractères)
✅ Vérification d'unicité (email et username)
✅ Sessions avec expiration (24h)

### Améliorations recommandées pour la production

- [ ] Utiliser bcrypt au lieu de SHA256
- [ ] Salt unique par utilisateur
- [ ] Rate limiting sur les endpoints d'auth
- [ ] Tokens JWT au lieu de UUID simples
- [ ] Refresh tokens
- [ ] Vérification email (envoi d'email de confirmation)
- [ ] Réinitialisation de mot de passe
- [ ] 2FA (authentification à deux facteurs)

## 📋 Erreurs possibles

| Code | Erreur | Solution |
|------|--------|----------|
| 400 | "Un compte avec cet email existe déjà" | Utiliser un autre email ou se connecter |
| 400 | "Ce nom d'utilisateur est déjà pris" | Choisir un autre username |
| 401 | "Email ou mot de passe incorrect" | Vérifier les identifiants |
| 422 | Validation error | Vérifier le format des données |

## 🎯 Prochaines étapes

Après l'authentification, l'utilisateur peut:

1. **Compléter son profil** → `/api/onboarding/start`
2. **Analyser des assiettes** → `/api/analyze/plate`
3. **Voir son historique** → `/api/analyze/history`
4. **Consulter ses stats** → `/api/session/stats/{user_id}`

Tous ces endpoints nécessitent le header `X-Session-Token` !
