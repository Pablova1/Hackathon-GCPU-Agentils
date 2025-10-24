# Tests - Changelog des corrections

## 📅 19 octobre 2025

### 🔧 Corrections appliquées

#### 1. **Organisation des fichiers de test**
- ✅ Déplacé tous les fichiers `test_*.py` vers `tests/`
- ✅ Créé `tests/services/` pour les tests de services
- ✅ Déplacé `test_nutrient_summary.py` vers `tests/services/`

#### 2. **Correction des imports Python**
**Problème:** `ModuleNotFoundError: No module named 'app'`

**Cause:** Après déplacement des tests vers `tests/`, Python ne trouvait plus le module `app/`

**Solution:** Ajout de `sys.path` dans chaque fichier de test :
```python
import sys
from pathlib import Path

# Ajouter le dossier backend au path pour permettre les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Maintenant les imports fonctionnent
from app.db.mongo_client import get_database
```

**Fichiers corrigés:**
- ✅ `test_agent_onboarding.py`
- ✅ `test_complete_onboarding.py`
- ✅ `test_user_collection.py`
- ✅ `test_mapping.py`

#### 3. **Correction des chemins `.env`**

**Problème:** Les agents cherchaient `.env` dans `backend/.env` au lieu de la racine

**Solution:** Ajouté un `.parent` supplémentaire pour remonter à la racine du projet

**Fichiers corrigés:**
- ✅ `app/ai/agents/agent_onboarding/agent.py` (5 → 6 parents)
- ✅ `app/ai/agents/agent_assiette_0/agent.py` (5 → 6 parents)
- ✅ `app/ai/agents/agent_assiette_1/agent.py` (5 → 6 parents)

**Navigation des chemins:**
```python
# Depuis agent_onboarding/agent.py
# agent.py 
# → agent_onboarding/ (parent 1)
# → agents/ (parent 2)
# → ai/ (parent 3)
# → app/ (parent 4)
# → backend/ (parent 5)
# → PROJECT_ROOT/ (parent 6) ← .env est ici !
```

#### 4. **Correction du chemin dans test_agent_onboarding.py**

**Avant:**
```python
env_path = Path(__file__).parent.parent / ".env"  # backend/.env ❌
```

**Après:**
```python
env_path = Path(__file__).parent.parent.parent / ".env"  # PROJECT_ROOT/.env ✅
```

---

## ✅ Tests validés

### Tests unitaires (sans serveur)
| Test | Status | Commentaire |
|------|--------|-------------|
| `test_agent_onboarding.py` | ✅ PASS | Génère question IA |
| `test_mapping.py` | ✅ PASS | Mapping slots → profil |
| `test_user_collection.py` | ✅ PASS | Création dans MongoDB |

### Tests d'intégration (nécessitent le serveur)
| Test | Status | Commentaire |
|------|--------|-------------|
| `test_complete_onboarding.py` | ⚠️ SKIP | Serveur non démarré |
| `test_onboarding.py` | ⚠️ SKIP | Serveur non démarré |

---

## 📊 Résultats des tests

### ✅ `test_agent_onboarding.py`
```
✅ Fichier .env trouvé: C:\...\Hackathon-GCPU-Agentils\.env
✅ Variables d'environnement chargées
✅ Agent initialisé avec succès
✅ Question IA générée: "Sophie, en tant que végétarienne très active, 
   quels sont tes principaux défis pour t'assurer d'avoir tous les 
   nutriments essentiels ?"
```

### ✅ `test_mapping.py`
```
✅ firstName présent
✅ lastName présent
✅ gender présent
✅ age calculé
✅ activityLevel présent
✅ diet présent
✅ notes avec réponses IA
```

### ✅ `test_user_collection.py`
```
✅ Utilisateur créé avec l'ID: 68f51df354d45f091b213b41
✅ Dans collection 'user': OUI
✅ Dans collection 'users': NON
📈 Collection 'user': 11 documents
```

---

## 🚀 Exécution des tests

### Depuis le dossier `backend/`
```bash
cd backend

# Tests unitaires (fonctionnent immédiatement)
python tests/test_agent_onboarding.py
python tests/test_mapping.py
python tests/test_user_collection.py

# Tests d'intégration (nécessitent le serveur)
# 1. Démarrer le serveur dans un terminal
python run.py

# 2. Dans un autre terminal
python tests/test_complete_onboarding.py
python tests/test_onboarding.py
```

### Avec pytest (recommandé)
```bash
pip install pytest pytest-asyncio

# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_agent_onboarding.py -v
pytest tests/services/ -v
```

---

## 🔍 Fichiers vérifiés (chemins `.env` corrects)

| Fichier | Chemin .env | Parents | Status |
|---------|-------------|---------|--------|
| `app/db/mongo_client.py` | ✅ Racine | 4 | OK |
| `app/core/config.py` | ✅ Racine | via BASE_DIR.parent | OK |
| `app/ai/agents/agent_onboarding/agent.py` | ✅ Racine | 6 | Corrigé |
| `app/ai/agents/agent_assiette_0/agent.py` | ✅ Racine | 6 | Corrigé |
| `app/ai/agents/agent_assiette_1/agent.py` | ✅ Racine | 6 | Corrigé |
| `tests/test_agent_onboarding.py` | ✅ Racine | 3 | Corrigé |

---

## 📝 Notes importantes

1. **Tous les agents chargent maintenant `.env` depuis la racine du projet**
2. **Tous les tests ont `sys.path` configuré pour importer depuis `app/`**
3. **Structure cohérente dans tous les fichiers**
4. **MongoDB Atlas fonctionne correctement**
5. **API Gemini répond (Google AI endpoint, pas Vertex AI)**

---

## 🎯 Prochaines étapes recommandées

1. ✅ Exécuter pytest pour automatiser les tests
2. ✅ Ajouter une CI/CD pour exécuter les tests automatiquement
3. ✅ Créer des fixtures pytest pour les données de test
4. ✅ Ajouter coverage report (pytest-cov)
5. ✅ Documenter les nouveaux tests ajoutés

---

**Date de mise à jour:** 19 octobre 2025, 19:20  
**Auteur:** Équipe Agentils
