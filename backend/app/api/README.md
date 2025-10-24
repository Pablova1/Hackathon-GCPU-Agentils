# Architecture des Routes API

## 📁 Structure

```
app/api/
├── main.py                    # Point d'entrée FastAPI principal
└── routes/                    # Tous les routers de l'API
    ├── __init__.py           # Agrège tous les routers (api_router)
    ├── analyze.py            # Routes d'analyse d'assiette
    ├── onboarding.py         # Routes d'onboarding utilisateur
    └── profile.py            # Routes de gestion de profil
```

## 🔗 Flux de routage

```
Client
  ↓
main.py (app FastAPI)
  ↓
app.include_router(api_router, prefix="/api")
  ↓
routes/__init__.py (api_router)
  ├── /analyze/*    → analyze.py
  ├── /onboarding/* → onboarding.py
  └── /profile/*    → profile.py
```

## 📋 Endpoints disponibles

### 🏠 Routes racines (sans /api)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Page d'accueil avec liste des endpoints |
| GET | `/health` | Health check global |
| GET | `/docs` | Documentation Swagger UI |
| GET | `/redoc` | Documentation ReDoc |

### 🍽️ Analyse d'assiette (`/api/analyze`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze/plate` | Analyse une photo d'assiette |
| POST | `/api/analyze/nutrients` | Analyse les nutriments d'aliments |
| GET | `/api/analyze/health` | Health check du service d'analyse |

**Fichier:** `app/api/routes/analyze.py`

### 👤 Onboarding (`/api/onboarding`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/onboarding/start` | Démarre une session d'onboarding |
| POST | `/api/onboarding/answer` | Enregistre une réponse et retourne la prochaine question |

**Fichier:** `app/api/routes/onboarding.py`

**Agent IA utilisé:** `agent_onboarding` (génération de questions personnalisées)

### 📝 Profil (`/api/profile`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/profile/start` | Crée un profil utilisateur complet |

**Fichier:** `app/api/routes/profile.py`

## 🎯 Principes de conception

### 1. Centralisation
- **Tous les routers** sont dans `app/api/routes/`
- **Un seul point d'agrégation** : `routes/__init__.py`
- **Préfixe uniforme** : Tous les endpoints ont le préfixe `/api`

### 2. Séparation des responsabilités

```python
# main.py - Configuration globale
- FastAPI app
- CORS middleware
- Logging
- Event handlers
- Routes racines (/, /health)

# routes/__init__.py - Agrégation
- Importe tous les routers
- Définit les préfixes
- Définit les tags

# routes/*.py - Logique métier
- Définit les endpoints
- Logique de traitement
- Appels aux services/agents
```

### 3. Convention de nommage

```python
# Dans chaque fichier de routes/
router = APIRouter()  # Pas de préfixe ici

# Les préfixes et tags sont définis dans __init__.py
api_router.include_router(
    router,
    prefix="/nom_du_module",
    tags=["Tag"]
)
```

## 📝 Ajouter un nouveau module

Pour ajouter un nouveau module de routes (ex: `/api/meals`) :

### 1. Créer le fichier de routes

**`app/api/routes/meals.py`:**
```python
"""
Routes pour la gestion des repas.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_meals():
    """Liste tous les repas."""
    return {"meals": []}

@router.post("/")
async def create_meal(meal_data: dict):
    """Crée un nouveau repas."""
    return {"message": "Repas créé"}
```

### 2. Ajouter au router principal

**`app/api/routes/__init__.py`:**
```python
from .meals import router as meals_router

api_router.include_router(
    meals_router,
    prefix="/meals",
    tags=["Repas"]
)
```

✅ **C'est tout !** Les endpoints sont automatiquement disponibles :
- `GET /api/meals/`
- `POST /api/meals/`

## 🔍 Exemples d'utilisation

### Démarrer un onboarding

```bash
curl -X POST "http://localhost:8000/api/onboarding/start?user_id=user123"
```

### Analyser une assiette

```bash
curl -X POST "http://localhost:8000/api/analyze/plate" \
  -F "file=@photo.jpg"
```

### Créer un profil

```bash
curl -X POST "http://localhost:8000/api/profile/start" \
  -H "Content-Type: application/json" \
  -d '{"firstName": "Sophie", ...}'
```

## 🧪 Tests

### Test des imports
```bash
python -c "from app.api.main import app; print('✅ OK')"
```

### Test du serveur
```bash
python run.py
# Accéder à http://localhost:8000/docs
```

### Test d'un endpoint
```bash
curl http://localhost:8000/health
```

## 📚 Documentation interactive

Une fois le serveur lancé :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

Ces interfaces listent automatiquement tous les endpoints avec :
- Paramètres requis
- Schémas de données
- Exemples de requêtes
- Codes de réponse

## ✅ Avantages de cette architecture

1. **Clarté** : Structure logique et prévisible
2. **Maintenabilité** : Facile d'ajouter/modifier des routes
3. **Cohérence** : Même pattern pour tous les modules
4. **Documentation** : Auto-générée par FastAPI
5. **Testabilité** : Chaque module peut être testé indépendamment
6. **Scalabilité** : Facile d'ajouter de nouveaux modules

---

**Date de restructuration** : 19 octobre 2025  
**Version** : 1.0.0
