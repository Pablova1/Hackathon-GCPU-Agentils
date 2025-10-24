# Tests - Food Analyzer API

## 📁 Structure

```
tests/
├── __init__.py
├── test_onboarding.py              # Tests de base du processus d'onboarding
├── test_complete_onboarding.py     # Test E2E complet avec questions IA
├── test_agent_onboarding.py        # Test spécifique de l'agent onboarding
├── test_mapping.py                 # Tests du mapping de données
├── test_user_collection.py         # Tests des collections utilisateur MongoDB
└── services/
    ├── __init__.py
    └── test_nutrient_summary.py    # Tests du service d'analyse nutritionnelle
```

## 🧪 Types de tests

### Tests d'intégration (E2E)

#### `test_complete_onboarding.py`
Test complet du flux d'onboarding avec API réelle.

**Prérequis:**
- Backend en cours d'exécution sur `http://localhost:8000`
- MongoDB Atlas accessible

**Exécution:**
```bash
cd backend
python tests/test_complete_onboarding.py
```

**Ce qui est testé:**
- Démarrage d'une session d'onboarding
- Réponse aux 9 questions obligatoires
- Création de l'utilisateur dans MongoDB
- Génération de questions IA personnalisées
- Enregistrement des réponses IA
- Vérification des données dans MongoDB

**Résultat attendu:**
```
✅ Session créée
✅ 9 questions obligatoires répondues
✅ Utilisateur créé dans MongoDB
✅ Questions IA générées (optionnel)
```

---

#### `test_onboarding.py`
Tests de base du système d'onboarding.

**Exécution:**
```bash
cd backend
python tests/test_onboarding.py
```

---

### Tests unitaires

#### `test_agent_onboarding.py`
Test unitaire de l'agent d'onboarding avec diagnostic complet.

**Prérequis:**
- Variables d'environnement dans `.env` à la racine

**Exécution:**
```bash
cd backend
python tests/test_agent_onboarding.py
```

**Ce qui est testé:**
- Chargement des variables d'environnement
- Initialisation de l'agent onboarding
- Génération de questions IA via l'API Gemini
- Format de la réponse

**Sortie:**
```
📁 Chargement du .env
✅ Variables d'environnement chargées
🤖 Initialisation de l'agent...
✅ Agent initialisé avec succès
📋 Test de génération de question...
✅ Question générée avec succès!
```

---

#### `test_mapping.py`
Tests du mapping des données utilisateur.

**Exécution:**
```bash
cd backend
python tests/test_mapping.py
```

**Ce qui est testé:**
- Conversion des slots en profil utilisateur
- Validation des types de données
- Gestion des champs optionnels

---

#### `test_user_collection.py`
Tests des opérations MongoDB sur les collections utilisateur.

**Prérequis:**
- MongoDB accessible

**Exécution:**
```bash
cd backend
python tests/test_user_collection.py
```

**Ce qui est testé:**
- Création d'utilisateur
- Lecture d'utilisateur
- Mise à jour d'utilisateur
- Suppression d'utilisateur

---

### Tests de services

#### `tests/services/test_nutrient_summary.py`
Tests du service d'analyse nutritionnelle.

**Exécution:**
```bash
cd backend
python tests/services/test_nutrient_summary.py
```

**Ce qui est testé:**
- Calcul des nutriments totaux
- Agrégation des données nutritionnelles
- Format de sortie

---

## 🚀 Exécuter tous les tests

### Option 1 : Manuellement (un par un)

```bash
cd backend

# Tests E2E (nécessitent le backend en cours d'exécution)
python tests/test_complete_onboarding.py
python tests/test_onboarding.py

# Tests unitaires
python tests/test_agent_onboarding.py
python tests/test_mapping.py
python tests/test_user_collection.py

# Tests de services
python tests/services/test_nutrient_summary.py
```

### Option 2 : Avec pytest (recommandé)

**Installation:**
```bash
pip install pytest pytest-asyncio
```

**Exécution:**
```bash
cd backend

# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_agent_onboarding.py
pytest tests/services/

# Avec verbose
pytest tests/ -v

# Avec coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📝 Conventions

### Nommage des fichiers
- `test_*.py` - Tous les fichiers de test commencent par `test_`
- Tests unitaires à la racine de `tests/`
- Tests de modules dans des sous-dossiers (`services/`, etc.)

### Nommage des fonctions
```python
def test_function_name():
    """Description du test."""
    pass

async def test_async_function():
    """Test asynchrone."""
    pass
```

### Structure d'un test
```python
def test_something():
    """Test de quelque chose."""
    # Arrange - Préparation
    data = {...}
    
    # Act - Action
    result = do_something(data)
    
    # Assert - Vérification
    assert result == expected
```

---

## 🛠️ Ajouter un nouveau test

### 1. Créer le fichier

**`tests/test_mon_module.py`:**
```python
"""
Tests pour mon module.
"""
import pytest

def test_ma_fonction():
    """Test de ma fonction."""
    # Arrange
    input_data = "test"
    
    # Act
    result = ma_fonction(input_data)
    
    # Assert
    assert result == "expected"
```

### 2. Tests asynchrones

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test d'une fonction asynchrone."""
    result = await ma_fonction_async()
    assert result is not None
```

### 3. Tests avec fixtures

```python
@pytest.fixture
def sample_user():
    """Fixture pour un utilisateur de test."""
    return {
        "firstName": "Sophie",
        "lastName": "Martin"
    }

def test_with_fixture(sample_user):
    """Test utilisant une fixture."""
    assert sample_user["firstName"] == "Sophie"
```

---

## 🔍 Debug des tests

### Logs détaillés

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Print statements
```python
def test_debug():
    result = ma_fonction()
    print(f"Résultat: {result}")  # Visible avec pytest -s
    assert result
```

### Breakpoints
```python
def test_with_breakpoint():
    result = ma_fonction()
    import pdb; pdb.set_trace()  # Pause ici
    assert result
```

---

## ✅ Checklist avant commit

- [ ] Tous les tests passent localement
- [ ] Pas de tests commentés/désactivés sans raison
- [ ] Documentation ajoutée pour les nouveaux tests
- [ ] Variables sensibles (clés API) dans `.env`, pas en dur
- [ ] Tests indépendants (pas d'effets de bord)

---

## 📊 Coverage

Générer un rapport de couverture de code :

```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

---

## 🐛 Problèmes fréquents

### "Backend not running"
**Solution:** Démarrer le backend avec `python run.py`

### "MongoDB connection timeout"
**Solution:** Vérifier que `MONGO_URI` est correct dans `.env`

### "GOOGLE_API_KEY missing"
**Solution:** Ajouter `GOOGLE_API_KEY` dans `.env` à la racine

### "Import errors"
**Solution:** Exécuter depuis le dossier `backend/`:
```bash
cd backend
python tests/test_xxx.py
```

---

**Date:** 19 octobre 2025  
**Auteur:** Équipe Agentils
