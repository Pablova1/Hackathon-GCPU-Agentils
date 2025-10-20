# 🍽️ Frontend - Nutrition App

## 🎯 Vue d'ensemble

Application Next.js pour l'analyse nutritionnelle d'assiettes avec système d'authentification intégré.

## 📁 Structure

```
frontend/
├── pages/
│   ├── index.js          # Page principale (analyse d'assiettes)
│   └── auth.js           # Page d'authentification
├── styles/
│   └── Auth.module.css   # Styles pour la page d'auth
├── public/
│   └── test_auth.html    # Page de test HTML (référence)
├── components/           # Composants réutilisables
├── hooks/                # Custom hooks
└── utils/                # Fonctions utilitaires
```

## 🚀 Démarrage

### 1. Installer les dépendances

```bash
cd frontend
npm install
```

### 2. Démarrer le serveur de développement

```bash
npm run dev
```

L'application sera accessible sur : **http://localhost:3000**

### 3. S'assurer que le backend est démarré

```bash
cd ../backend
python run.py
```

Le backend doit être accessible sur : **http://localhost:8000**

## 🔐 Flux d'authentification

### 1. Page d'authentification (`/auth`)

Accessible sur : **http://localhost:3000/auth**

**Fonctionnalités :**
- ✅ Inscription de nouveaux utilisateurs
- ✅ Connexion d'utilisateurs existants
- ✅ Validation des formulaires
- ✅ Sauvegarde automatique du session_token dans localStorage
- ✅ Redirection automatique vers la page principale après authentification

### 2. Page principale (`/`)

Accessible sur : **http://localhost:3000**

**Protections :**
- ✅ Vérification de la session au chargement
- ✅ Redirection vers `/auth` si pas de session
- ✅ Ajout automatique du `X-Session-Token` dans toutes les requêtes
- ✅ Bouton de déconnexion
- ✅ Gestion de l'expiration de session (redirection auto vers `/auth`)

## 🔄 Flux complet

```
1. Utilisateur ouvre http://localhost:3000
   └─> Pas de session_token dans localStorage
   └─> Redirection automatique vers /auth

2. Utilisateur s'inscrit ou se connecte sur /auth
   └─> POST /api/auth/register ou /api/auth/login
   └─> Réception du session_token
   └─> Sauvegarde dans localStorage
   └─> Redirection automatique vers /

3. Sur la page principale (/)
   └─> Vérification de la session
   └─> Affichage du nom d'utilisateur
   └─> Analyse d'assiettes avec token dans headers

4. Toutes les requêtes incluent le token
   └─> Header: X-Session-Token: abc-123...
   └─> Backend identifie automatiquement l'utilisateur

5. Déconnexion
   └─> Suppression des données du localStorage
   └─> Redirection vers /auth
```

## 📝 Utilisation des données de session

Le système stocke dans `localStorage` :

```javascript
{
  session_token: "abc-123-def-456",
  user_id: "user_abc123",
  username: "Alice",
  email: "alice@example.com"
}
```

### Récupérer les données dans un composant

```javascript
import { useState, useEffect } from 'react';

export default function MonComposant() {
  const [sessionToken, setSessionToken] = useState(null);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('session_token');
    const user = localStorage.getItem('username');
    
    setSessionToken(token);
    setUsername(user);
  }, []);

  // Utiliser dans une requête
  const faireUneRequete = async () => {
    const res = await fetch('http://localhost:8000/api/analyze/plate', {
      method: 'POST',
      headers: {
        'X-Session-Token': sessionToken
      },
      body: formData
    });
  };
}
```

## 🛡️ Protection des routes

Toutes les pages nécessitant une authentification doivent inclure ce code :

```javascript
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function PageProtegee() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('session_token');
    if (!token) {
      router.push('/auth');
    }
  }, [router]);

  // ... reste du composant
}
```

## 🎨 Pages disponibles

### `/auth` - Authentification
- Formulaire de connexion
- Formulaire d'inscription
- Validation côté client
- Messages d'erreur et de succès
- Redirection automatique après auth

### `/` - Analyse d'assiettes (protégée)
- Upload d'image
- Détection des aliments
- Modification des quantités
- Analyse nutritionnelle
- Bouton de déconnexion
- Affichage du nom d'utilisateur

## 🔧 Configuration

### URLs de l'API

Les URLs sont actuellement en dur dans le code. Pour les modifier :

**Dans `pages/auth.js` :**
```javascript
const API_URL = 'http://localhost:8000/api';
```

**Dans `pages/index.js` :**
```javascript
const API_URL = 'http://localhost:8000/api';
```

### Variables d'environnement (recommandé)

Créez un fichier `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Puis utilisez :
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
```

## 🐛 Gestion des erreurs

### Erreur 401 (Session expirée)

Toutes les requêtes vérifient le code 401 et redirigent automatiquement :

```javascript
if (res.status === 401) {
  // Session expirée
  localStorage.clear();
  router.push('/auth');
  return;
}
```

### Erreur de connexion au serveur

```javascript
catch (err) {
  setError('Erreur de connexion au serveur. Vérifiez que l\'API est démarrée.');
}
```

## 📱 Responsive Design

Le design est responsive et fonctionne sur :
- ✅ Desktop (1920px+)
- ✅ Laptop (1366px - 1920px)
- ✅ Tablet (768px - 1366px)
- ✅ Mobile (< 768px)

## 🚀 Build pour production

```bash
# Build
npm run build

# Démarrer en production
npm start
```

## 🧪 Tests

### Tester l'authentification

1. Ouvrir **http://localhost:3000/auth**
2. S'inscrire avec un nouveau compte
3. Vérifier la redirection vers `/`
4. Vérifier que le nom s'affiche en haut à droite
5. Tester le bouton de déconnexion

### Tester l'analyse

1. Être connecté sur `/`
2. Uploader une image d'assiette
3. Vérifier que les aliments sont détectés
4. Modifier les quantités si nécessaire
5. Valider pour l'analyse nutritionnelle

### Tester la persistance de session

1. Se connecter
2. Fermer l'onglet
3. Rouvrir **http://localhost:3000**
4. → Devrait rester connecté (tant que la session n'a pas expiré)

### Tester l'expiration de session

1. Se connecter
2. Dans MongoDB, supprimer la session ou attendre 24h
3. Tenter une analyse
4. → Devrait rediriger vers `/auth` avec message d'erreur

## 📚 Prochaines étapes

- [ ] Ajouter une page de profil utilisateur
- [ ] Ajouter un historique des analyses
- [ ] Ajouter des graphiques nutritionnels
- [ ] Implémenter le "Remember me"
- [ ] Ajouter la réinitialisation de mot de passe
- [ ] Améliorer le design de la page principale
- [ ] Ajouter des transitions entre les pages
- [ ] Implémenter un système de notifications

## 🤝 Intégration avec le backend

Toutes les routes utilisées :

| Route | Méthode | Description | Headers requis |
|-------|---------|-------------|----------------|
| `/api/auth/register` | POST | Inscription | - |
| `/api/auth/login` | POST | Connexion | - |
| `/api/analyze/plate` | POST | Analyser assiette | X-Session-Token |
| `/api/analyze/nutrients` | POST | Analyser nutriments | X-Session-Token |
| `/api/analyze/history` | GET | Historique | X-Session-Token |

## 💡 Astuces

### Déboguer les sessions

Ouvrez la console du navigateur et tapez :
```javascript
// Voir toutes les données stockées
console.log({
  token: localStorage.getItem('session_token'),
  user_id: localStorage.getItem('user_id'),
  username: localStorage.getItem('username'),
  email: localStorage.getItem('email')
});

// Forcer une déconnexion
localStorage.clear();
window.location.reload();
```

### Tester avec différents utilisateurs

Ouvrez un navigateur en mode incognito ou utilisez différents navigateurs pour tester avec plusieurs comptes simultanément.
