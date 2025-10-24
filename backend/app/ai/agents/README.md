# Agents IA

Ce dossier contient tous les agents IA de l'application.

## Structure

Chaque agent est organisé dans son propre dossier avec la structure suivante :

```
agent_xxx/
├── __init__.py          # Export de l'agent
├── agent.py             # Implémentation de la classe Agent
└── README.md            # Documentation spécifique (optionnel)
```

**⚠️ Important:** Les fichiers `.env` individuels par agent ne sont plus utilisés. 
Toutes les variables d'environnement sont centralisées dans le fichier `.env` à la racine du projet.

## Agents disponibles

### 1. **agent_assiette_0** - Analyse de composition d'assiette
- **Classe:** `FoodAnalyzerAgent`
- **Fonction:** Analyse une image d'assiette et identifie les aliments présents avec leurs quantités
- **Input:** Image (PIL.Image ou chemin)
- **Output:** Liste des aliments avec quantités estimées

**Exemple:**
```python
from app.ai.agents.agent_assiette_0 import FoodAnalyzerAgent

agent = FoodAnalyzerAgent()
result = agent.analyze_plate("path/to/image.jpg")
# {'foods': [{'name': 'poulet', 'estimated_quantity': 150}, ...]}
```

### 2. **agent_assiette_1** - Analyse nutritionnelle
- **Classe:** `NutrientAnalyzerAgent`
- **Fonction:** Analyse les nutriments d'une liste d'aliments
- **Input:** Liste d'aliments avec quantités
- **Output:** Composition nutritionnelle détaillée (calories, protéines, etc.)

**Exemple:**
```python
from app.ai.agents.agent_assiette_1 import NutrientAnalyzerAgent

agent = NutrientAnalyzerAgent()
foods = [{"name": "poulet", "estimated_quantity": 150}]
nutrients = agent.analyze_nutrients(foods)
# {'total_calories': 248, 'proteins': 37.5, ...}
```

### 3. **agent_onboarding** - Questions personnalisées
- **Classe:** `OnboardingAgent`
- **Fonction:** Génère des questions personnalisées pendant l'onboarding
- **Input:** Contexte utilisateur (réponses déjà fournies)
- **Output:** Question de suivi pertinente

**Exemple:**
```python
from app.ai.agents.agent_onboarding import OnboardingAgent

agent = OnboardingAgent()
slots = {"firstName": "Sophie", "dietType": "vegetarian"}
question = agent.suggest_followup(slots, asked_ai_count=0)
# {'slot': 'ai_followup_0', 'text': 'Quels sont tes objectifs...', ...}
```

## Initialisation centralisée

Utilisez `agent_initializer.py` pour obtenir des instances singleton des agents :

```python
from app.ai.agents.agent_initializer import (
    get_food_analyzer,
    get_nutrient_analyzer,
    get_onboarding_agent
)

# Obtenir les instances (créées une seule fois)
food_agent = get_food_analyzer()
nutrient_agent = get_nutrient_analyzer()
onboarding_agent = get_onboarding_agent()
```

## Configuration

Toutes les variables d'environnement nécessaires sont dans le fichier `.env` à la racine :

```env
# API Google Gemini
GOOGLE_API_KEY=your_api_key_here

# Configuration GCP (pour Vertex AI)
GCP_PROJECT_ID=your_project_id
GCP_REGION=europe-west1

# Modèle Gemini
GEMINI_MODEL=gemini-2.5-flash

# Prompt système pour l'onboarding (optionnel)
AI_SYSTEM_PROMPT=Your custom prompt...
```

## Ajouter un nouvel agent

1. Créer un nouveau dossier `agent_xxx/`
2. Créer `__init__.py` qui exporte votre classe agent
3. Créer `agent.py` avec l'implémentation
4. Ajouter la fonction getter dans `agent_initializer.py`
5. Documenter dans ce README

**Template de base:**

```python
# agent_xxx/__init__.py
from .agent import MyAgent
__all__ = ["MyAgent"]

# agent_xxx/agent.py
class MyAgent:
    def __init__(self, api_key=None, load_env=True):
        if load_env:
            from pathlib import Path
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        # ... votre logique
```

## Architecture

```
app/ai/agents/
├── agent_initializer.py        # Gestion des singletons
├── README.md                    # Cette documentation
├── agent_assiette_0/           # Agent analyse d'image
│   ├── __init__.py
│   ├── agent.py
│   └── README.md
├── agent_assiette_1/           # Agent analyse nutritionnelle
│   ├── __init__.py
│   └── agent.py
└── agent_onboarding/           # Agent questions onboarding
    ├── __init__.py
    ├── agent.py
    └── README.md
```

## Notes importantes

- ✅ Tous les agents partagent la même clé API Google
- ✅ Les agents sont créés en singleton (une seule instance)
- ✅ Gestion des erreurs intégrée avec logging
- ✅ Compatible avec les anciens imports pour rétrocompatibilité
- ❌ Ne plus créer de fichiers `.env` dans les dossiers agents
 