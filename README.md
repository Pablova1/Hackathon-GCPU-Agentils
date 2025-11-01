# 🌱 Les Agentils - Plateforme de Nutrition Intelligente

[![GCP](https://img.shields.io/badge/Cloud-Google%20Cloud-blue)](https://cloud.google.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com)

## 📖 Description

MyPlate est une plateforme intelligente de nutrition personnalisée qui utilise l'IA pour analyser les habitudes alimentaires, fournir des recommandations sur mesure et accompagner les utilisateurs dans leur parcours de bien-être.

**🌐 Application déployée :**
- **Frontend** : https://agentils-frontend-807842718393.europe-west1.run.app
- **Backend API** : https://agentils-backend-807842718393.europe-west1.run.app

## 🏆 Contexte

Ce projet a été développé dans le cadre du **Hackathon GCPU (Google Cloud Platform University)** organisé par Google. Notre équipe des Agentils a relevé le défi de créer une solution innovante utilisant les technologies Google Cloud Platform et l'intelligence artificielle pour améliorer le bien-être nutritionnel des utilisateurs.

## 🚀 Lancement Rapide

### Développement Local

**Backend :**
```bash
cd backend
python run.py
```

**Frontend :**
```bash
cd frontend
npm run dev
```

### Avec Docker

```bash
# Lancer tous les services
docker-compose up --build

# Rebuild le frontend sans cache
docker-compose build --no-cache frontend

# Voir les conteneurs en cours d'exécution
docker ps -a

# Arrêter les conteneurs
docker-compose down
```

### 🎯 Fonctionnalités principales

- **Onboarding intelligent** : Questionnaire de 27 questions en anglais géré par IA pour créer un profil nutritionnel complet
- **Analyse automatique des repas** : Reconnaissance d'images IA (Google Gemini Vision) pour tracker l'alimentation
- **Chatbot nutritionnel** : Assistant IA conversationnel avec historique pour un suivi personnalisé
- **Score hebdomadaire** : Évaluation automatique de la qualité nutritionnelle sur 7 jours
- **Recommandations personnalisées** : Suggestions de repas adaptées au profil et aux objectifs
- **Questions IA dynamiques** : Génération de questions personnalisées après l'onboarding
---

## 🏗️ Architecture Technique

### Stack Technologique

```
Frontend     : Next.js 15.5 + React
Backend      : FastAPI + Python 3.11
Database     : MongoDB Atlas (NoSQL)
AI/ML        : Google Gemini 2.0 Flash (generativelanguage API)
Auth         : Custom JWT + Session Management
Storage      : Local uploads + MongoDB
Hosting      : Google Cloud Run
Registry     : Google Artifact Registry
CI/CD        : Docker + gcloud CLI
Monitoring   : Google Cloud Logging
```


## 🚀 Installation et Développement

### Prérequis

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **Docker** >= 24.0.0
- **Google Cloud CLI** (gcloud)
- **Git**
- **MongoDB Atlas Account**

---

## 👥 Équipe

**Les Agentils** - Hackathon GCPU 2025

- **Natalia Gérard**
- **Héloïse Roméo**
- **Paul Ranc**
- **Valentin Templé**
- **Valentin Rech**

---

**Développé avec ❤️ par l'équipe des Agentils lors du Hackathon GCPU 2025**