# Agent Onboarding

## Description

L'agent d'onboarding génère des questions personnalisées pendant le processus d'inscription pour enrichir le profil utilisateur. Il utilise Google Gemini via Vertex AI pour analyser les réponses déjà fournies et suggérer des questions de suivi pertinentes.

## Fonctionnalités

- ✅ Génération de questions contextuelles basées sur les réponses utilisateur
- ✅ Limitation du nombre de questions (3 par défaut)
- ✅ Intégration avec Google Gemini via Vertex AI
- ✅ Logging détaillé pour le debugging
- ✅ Gestion des erreurs et timeouts

## Configuration

### Variables d'environnement requises

```env
# Clé API Google (prioritaire)
GOOGLE_API_KEY=your_api_key_here

# OU ancienne configuration
API_KEY=your_api_key_here

# Configuration GCP (optionnel pour Vertex AI)
GCP_PROJECT_ID=your_project_id
GCP_REGION=europe-west1

# Prompt système personnalisé (optionnel)
AI_SYSTEM_PROMPT=Your custom prompt here...
```

## Utilisation

### Import simple

```python
from app.ai.agents.agent_onboarding import OnboardingAgent

# Créer une instance de l'agent
agent = OnboardingAgent()

# Générer une question de suivi
slots = {
    "firstName": "Sophie",
    "age": 28,
    "dietType": "vegetarian"
}

question = agent.suggest_followup(slots, asked_ai_count=0)
if question:
    print(f"Question suggérée: {question['text']}")
```

### Utilisation avec l'API de compatibilité

```python
from app.ai.agents.agent_onboarding.agent import suggest_followup

# Utiliser la fonction de compatibilité (comme l'ancien code)
question = suggest_followup(slots, asked_ai_count=0)
```

### Configuration personnalisée

```python
agent = OnboardingAgent(
    api_key="your_custom_key",
    project_id="your_project",
    region="us-central1",
    max_questions=5,  # Changer le nombre max de questions
    system_prompt="Your custom prompt..."
)
```

## Architecture

```
agent_onboarding/
├── __init__.py          # Export de l'agent
├── agent.py             # Implémentation de OnboardingAgent
└── README.md            # Cette documentation
```

## Intégration dans le flux d'onboarding

L'agent est appelé automatiquement après que l'utilisateur a répondu à toutes les questions obligatoires. Il peut générer jusqu'à 3 questions supplémentaires pour enrichir le profil.

**Flux:**
1. Utilisateur répond aux 9 questions obligatoires
2. Profil utilisateur créé dans MongoDB
3. Agent onboarding génère une première question IA
4. Utilisateur peut répondre ou passer
5. Répéter jusqu'à 3 questions max ou fin de l'onboarding

## Exemples de questions générées

Selon le contexte utilisateur, l'agent peut poser:
- "Quels sont tes objectifs nutritionnels pour les prochains mois ?"
- "As-tu des allergies ou intolérances alimentaires ?"
- "Combien de repas prends-tu par jour en moyenne ?"
- "Pratiques-tu un sport particulier ?"

## Logs et Debug

L'agent utilise le module `logging` de Python. Pour voir les logs détaillés:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Gestion des erreurs

L'agent gère gracieusement:
- ❌ Timeouts API (20s par défaut)
- ❌ Erreurs de connexion
- ❌ Réponses API malformées
- ❌ Clés API manquantes

En cas d'erreur, l'agent retourne `None` au lieu de crasher.
