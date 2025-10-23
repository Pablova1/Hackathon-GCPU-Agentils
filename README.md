# 🌱 Les Agentils - Plateforme de Nutrition Intelligente

[![GCP](https://img.shields.io/badge/Cloud-Google%20Cloud-blue)](https://cloud.google.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)

## 📖 Description

Les Agentils on fait une plateforme intelligente de nutrition personnalisée qui utilise l'IA pour analyser les habitudes alimentaires, fournir des recommandations sur mesure et accompagner les utilisateurs dans leur parcours de bien-être.

## Lancement Backend
cd backend
python run.py

## Lancement Frontend
cd frontend
npm run dev

## Lancement avec Docker
docker-compose up --build
docker-compose build --no-cache frontend ## Pour refresh le cache du front

## Voir les conteneurs en cours d'execution
docker ps -a

## Arreter les conteneurs Docker en cours d'exécution
docker-compose down
docker stop $(docker ps -q)

### 🎯 Fonctionnalités principales

- **Onboarding intelligent** : Questionnaire adaptatif géré par IA pour créer un profil nutritionnel personnalisé
- **Analyse automatique des repas** : Reconnaissance d'images IA pour tracker l'alimentation sans effort
- **Chatbot nutritionnel** : Assistant vocal et textuel pour un suivi quotidien (conversations de 2min/jour)
- **Recommandations personnalisées** : Conseils adaptatifs basés sur le profil et l'évolution de l'utilisateur
---

## 🏗️ Architecture Technique

### Stack Technologique

```
Frontend     : Next.js + TypeScript + PWA
Backend      : FastAPI + Python 3.11
Database     : Firestore + Cloud SQL (PostgreSQL)
AI/ML        : Vertex AI + Dialogflow CX
Auth         : Firebase Authentication
Storage      : Cloud Storage
Hosting      : Firebase Hosting + Cloud Run
CI/CD        : Cloud Build + GitHub Actions
Monitoring   : Cloud Monitoring + Cloud Logging
```

### Architecture des Services

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js PWA)                   │
├─────────────────────────────────────────────────────────────┤
│                    Firebase Auth                            │
├─────────────────────────────────────────────────────────────┤
│  API Gateway (Cloud Endpoints) + Load Balancer              │
├─────────────────────────────────────────────────────────────┤
│  Microservices (Cloud Run)                                  │
│  ┌─────────────┬──────────────┬─────────────┬──────────────┐│
│  │User Service │ Meal Service │Chat Service │Reco Service  ││
│  └─────────────┴──────────────┴─────────────┴──────────────┘│
├─────────────────────────────────────────────────────────────┤
│  AI Services (Vertex AI)                                    │
│  ┌───────────────┬──────────────┬──────────────────────────┐│
│  │Gemini 2.5 Pro │Speech-to-Text│    Dialogflow CX         ││
│  └───────────────┴──────────────┴──────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────┬──────────────┬────────────────────────────┐│
│  │ Firestore   │  Cloud SQL   │   Cloud Storage            ││
│  │(NoSQL)      │(PostgreSQL)  │   (Images/Audio)           ││
│  └─────────────┴──────────────┴────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation et Développement

### Prérequis

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **Docker** >= 24.0.0
- **Google Cloud CLI** (gcloud)
- **Git**

### Configuration initiale

1. **Cloner le repository**
```bash
git clone https://github.com/Pablova1/Hackathon-GCPU-Agentils.git
cd Hackathon-GCPU-Agentils
```

2. **Configuration Google Cloud**
```bash
gcloud auth login
gcloud config set project your-project-id
gcloud auth application-default login
```


---

## 📁 Structure du Projet

```
Hackathon-GCPU-Agentils/
├── 📁 frontend/                 # Application Next.js
│   ├── 📁 components/          # Composants React
│   ├── 📁 pages/               # Pages Next.js
│   ├── 📁 hooks/               # Custom hooks
│   ├── 📁 utils/               # Utilitaires
│   ├── 📁 styles/              # Styles CSS/SCSS
│   └── 📁 public/              # Assets statiques
├── 📁 backend/                 # API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 api/             # Endpoints API
│   │   ├── 📁 core/            # Configuration
│   │   ├── 📁 models/          # Modèles de données
│   │   ├── 📁 services/        # Logique métier
│   │   ├── 📁 db/              # Base de données
│   │   └── 📁 ai/              # Services IA
│   ├── 📁 tests/               # Tests unitaires
│   └── 📁 migrations/          # Migrations DB
├── 📁 infrastructure/          # Configuration GCP
│   ├── 📁 terraform/           # Infrastructure as Code
│   ├── 📁 k8s/                 # Kubernetes manifests
│   └── 📁 docker/              # Dockerfiles
├── 📁 docs/                    # Documentation
├── 📁 scripts/                 # Scripts de déploiement
├── .github/workflows/          # CI/CD GitHub Actions
├── docker-compose.yml          # Développement local
└── README.md                   # Ce fichier
```

---


## 📚 API Documentation

### Endpoints principaux (à modifier au dev)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/v1/auth/register` | POST | Inscription utilisateur | ❌ |
| `/api/v1/auth/login` | POST | Connexion | ❌ |
| `/api/v1/users/profile` | GET/PUT | Profil utilisateur | ✅ |
| `/api/v1/meals/analyze` | POST | Analyse photo repas | ✅ |
| `/api/v1/chat/conversation` | POST | Conversation chatbot | ✅ |
| `/api/v1/recommendations` | GET | Recommandations | ✅ |
| `/api/v1/health` | GET | Health check | ❌ |


### Exemples d'utilisation

#### Analyse d'un repas

```bash
curl -X POST "https://api.Hackathon-GCPU-Agentils.com/api/v1/meals/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@meal.jpg"
```

#### Conversation avec le chatbot

```bash
curl -X POST "https://api.Hackathon-GCPU-Agentils.com/api/v1/chat/conversation" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Comment je me sens aujourd'\''hui ?",
    "audio_data": "base64_audio_data"
  }'
```

---

## 🤝 Contribution

### Workflow de développement

1. **Fork** le projet
2. **Créer une branche** (`git checkout -b feature/amazing-feature`)
3. **Commiter** (`git commit -m 'Add amazing feature'`)
4. **Push** (`git push origin feature/amazing-feature`)
5. **Créer une Pull Request**


---

### Commits conventionnels

```
feat: add meal photo analysis
fix: resolve authentication bug
docs: update API documentation
style: format code with black
refactor: optimize database queries
test: add unit tests for user service
chore: update dependencies
```


---

## 🌍 Internationalisation (Il faudrait, dimension mondial)

### Langues supportées

- 🇫🇷 **Français** (défaut)
- 🇬🇧 **Anglais**

### Configuration i18n

```bash
# Ajouter une traduction
cd frontend
npm run i18n:extract
npm run i18n:translate
```

---


**Développé avec ❤️ par l'équipe des Agentils**