# 🚀 GUIDE SIMPLE : DÉPLOYER SUR CLOUD RUN

## ✨ C'est facile : juste 5 commandes !

### 1️⃣ PRÉPARATION (5 min)

```bash
# Se connecter à GCP
gcloud auth login

# Choisir ton projet (créer d'abord sur console.cloud.google.com)
gcloud config set project YOUR-PROJECT-ID

# Vérifier que tu es connecté
gcloud config list
```

### 2️⃣ DÉPLOYER LE BACKEND (2 min)

```bash
# Depuis la racine du projet
cd Hackathon-GCPU-Agentils

# Build et déploie automatiquement
gcloud run deploy agentils-backend \
    --source ./backend \
    --platform managed \
    --region eu-west1 \
    --allow-unauthenticated \
    --port 8000 \
    --memory 512Mi
```

**Output:**
```
Service URL: https://agentils-backend-xxxxx-ew.a.run.app
✓ Deployment complete!
```

**COPIE CETTE URL** → Tu en auras besoin pour le frontend

### 3️⃣ DÉPLOYER LE FRONTEND (2 min)

```bash
# Remplace XXX par l'URL du backend
gcloud run deploy agentils-frontend \
    --source ./frontend \
    --platform managed \
    --region eu-west1 \
    --allow-unauthenticated \
    --port 3000 \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://agentils-backend-xxxxx-ew.a.run.app"
```

**Output:**
```
Service URL: https://agentils-frontend-xxxxx-ew.a.run.app
✓ Deployment complete!
```

**VOILÀ !** Ton app est live ! 🎉

---

## 📊 C'est GRATUIT !

Cloud Run donne **2 millions d'invocations gratuites par mois**
(À moins que tu ais 1M visites/jour, c'est gratuit)

---

## 🔧 COMMANDES UTILES

### Voir les logs en temps réel
```bash
# Backend
gcloud run logs read agentils-backend --limit 100 --follow

# Frontend
gcloud run logs read agentils-frontend --limit 100 --follow
```

### Mettre à jour l'app
```bash
# Juste redéployer (même commande qu'avant)
gcloud run deploy agentils-backend \
    --source ./backend \
    --platform managed \
    --region eu-west1
```

### Voir les services déployés
```bash
gcloud run services list
```

### Supprimer un service
```bash
gcloud run services delete agentils-backend --region eu-west1
```

---

## ⚠️ POINTS IMPORTANTS

### Variables d'environnement
Si tu as besoin de secrets (API keys, DB URLs...) :

```bash
# Créer un secret
gcloud secrets create my-secret --data-file=- <<< "my-value"

# L'utiliser lors du déploiement
gcloud run deploy agentils-backend \
    --source ./backend \
    --platform managed \
    --region eu-west1 \
    --update-secrets "MONGODB_URI=my-secret:latest"
```

### Taille mémoire
- **Frontend**: 256Mi (parfait pour une app Next.js)
- **Backend**: 512Mi ou 1Gi (dépend de tes calculs IA)

### Cold start
Premier appel peut être lent (2-5 sec) si l'app a pas eu d'appels depuis longtemps.
Solution: Keep-alive externe (gratuit avec healthchecks)

---

## 🧪 AVANT DE DÉPLOYER

Teste localement d'abord :

```bash
# Build l'image localement
cd backend
docker build -t agentils-backend .
docker run -p 8000:8000 agentils-backend

# Dans un autre terminal
curl http://localhost:8000/health
```

---

## 📱 CUSTOM DOMAIN (optionnel)

```bash
# Après déploiement
gcloud run services update agentils-backend \
    --region eu-west1 \
    --update-env-vars "CUSTOM_DOMAIN=api.lesagentils.com"

# Configurer DNS chez ton registrar (Namecheap, Google Domains...)
# Pointer vers: ghs.googleusercontent.com
```

---

## 🎯 RÉSUMÉ

| Étape | Temps | Commande |
|-------|-------|----------|
| Setup | 5 min | `gcloud auth login` |
| Backend | 2 min | `gcloud run deploy agentils-backend --source ./backend ...` |
| Frontend | 2 min | `gcloud run deploy agentils-frontend --source ./frontend ...` |
| **TOTAL** | **9 min** | ✅ |

---

Besoin d'aide ? 🤔
