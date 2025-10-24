# Simplification des Sessions - Migration de `user_sessions` vers `user`

**Date:** 21 octobre 2025  
**Objectif:** Simplifier l'architecture en intégrant les sessions directement dans la collection `user`

---

## 🎯 Changements Effectués

### 1. Modèle de données (`profile_model.py`)
Ajout des champs de session directement dans `UserDocument` :
- `session_token` : Token UUID de la session active
- `session_created_at` : Date de création de la session
- `session_expires_at` : Date d'expiration (24h après création)
- `last_activity` : Dernière activité de l'utilisateur

### 2. SessionManager (`session_manager.py`)
**Avant :** Utilisait une collection séparée `user_sessions`  
**Après :** Utilise directement la collection `user`

#### Méthodes modifiées :
- `create_user_session(user_id)` : Met à jour le document user avec un nouveau token
- `get_session(session_token)` : Récupère l'utilisateur par son token et vérifie l'expiration
- `mark_onboarding_complete(user_id)` : Marque `profile_completed = True`
- `get_user_stats(user_id)` : Retourne les stats depuis le document user

#### Méthodes supprimées :
- `update_session_metadata()` : N'est plus nécessaire

#### Nouvelles méthodes :
- `revoke_session(user_id)` : Supprime le token de session (logout)

### 3. Routes d'authentification (`auth.py`)
- **Register** : Crée le token de session directement lors de l'inscription
- **Login** : Renouvelle le token à chaque connexion (invalidant l'ancienne session)
- **Logout** : Révoque le token côté serveur (supprime du document user)

### 4. Autres routes
- `analyze.py` : Suppression de `update_session_metadata()`
- `session.py` : Mise à jour pour refléter la nouvelle structure

---

## ✅ Avantages de cette simplification

### Pour le développement (Hackathon)
- ✅ **Moins de requêtes** : Une seule requête au lieu de deux (user + session)
- ✅ **Architecture simplifiée** : Une collection en moins à gérer
- ✅ **Code plus clair** : Logique centralisée dans le document user

### Limitations acceptées
- ⚠️ **Une session à la fois** : Se connecter ailleurs déconnecte l'autre appareil
- ⚠️ **Pas d'historique** : Pas de trace des anciennes sessions

---

## 🔄 Migration des données existantes

Si vous aviez des utilisateurs avec l'ancien système :

```javascript
// Script MongoDB pour nettoyer les anciennes sessions
db.user_sessions.drop();  // Supprimer l'ancienne collection

// Tous les utilisateurs devront se reconnecter
// (leurs tokens seront créés automatiquement au login)
```

---

## 📝 Structure du document User (après modification)

```json
{
  "user_id": "user_abc123",
  "password_hash": "...",
  
  // SESSION (nouveau)
  "session_token": "uuid-token-here",
  "session_created_at": "2025-10-21T10:00:00",
  "session_expires_at": "2025-10-22T10:00:00",
  "last_activity": "2025-10-21T15:30:00",
  
  // PROFIL
  "profile": {
    "firstName": "Alice",
    "lastName": "Martin",
    "email": "alice@example.com",
    "age": 25,
    "gender": "Female",
    "weight": 60.0,
    "height": 165.0
  },
  
  // AUTRES SECTIONS
  "medical": {...},
  "nutrition": {...},
  "goals": {...},
  
  // METADATA
  "created_at": "2025-10-20T08:00:00",
  "last_login": "2025-10-21T10:00:00",
  "profile_completed": true
}
```

---

## 🔐 Sécurité

- Les sessions expirent après **24 heures**
- Le logout révoque le token côté serveur
- Chaque connexion génère un nouveau token (invalide l'ancien)

---

## 🚀 Utilisation

### Inscription
```bash
POST /api/auth/register
{
  "email": "alice@example.com",
  "password": "motdepasse",
  "first_name": "Alice",
  "last_name": "Martin"
}

# Retourne : session_token à utiliser dans les headers
```

### Connexion
```bash
POST /api/auth/login
{
  "email": "alice@example.com",
  "password": "motdepasse"
}

# Retourne : nouveau session_token (invalide l'ancien)
```

### Déconnexion
```bash
POST /api/auth/logout?session_token=abc-123-def
```

### Utilisation dans les requêtes
```bash
GET /api/session/info
Headers:
  X-Session-Token: votre-token-ici
```

---

## 📚 Fichiers modifiés

1. `backend/app/models/profile_model.py` - Ajout des champs session
2. `backend/app/middleware/session_manager.py` - Simplification complète
3. `backend/app/api/routes/auth.py` - Création de session intégrée
4. `backend/app/api/routes/analyze.py` - Suppression update_session_metadata
5. `backend/app/api/routes/session.py` - Adaptation aux nouvelles sessions

---

## 🎓 Pour aller plus loin

Si vous aviez besoin de **multi-sessions** (plusieurs appareils simultanés) :
- Utilisez un array `sessions: []` dans le document user
- Chaque élément contient `{token, created_at, expires_at, device_info}`
