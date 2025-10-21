# Agent Weekly Score

Agent IA pour calculer une note hebdomadaire basée sur les repas scannés.

## Fonctionnalités

- Analyse les repas des 7 derniers jours
- Génère une note de 1 à 5
- Fournit un commentaire encourageant et personnalisé
- Évalue la variété, l'équilibre nutritionnel et la présence de fruits/légumes

## Utilisation

```python
from app.ai.agents.agent_weekly_score import WeeklyScoreAgent

# Initialiser l'agent
agent = WeeklyScoreAgent()

# Calculer le score
meals = [...]  # Liste des repas de la semaine
result = agent.calculate_score(meals)

print(f"Score: {result['score']}/5")
print(f"Commentaire: {result['comment']}")
```

## Format des repas

Chaque repas doit contenir :
```python
{
    "name": "Nom du repas",
    "ingredients": ["ingrédient1", "ingrédient2"],
    "nutrients": {
        "calories": 450.0,
        "protein": 35.0,
        "carbohydrates": 45.0,
        "fat": 12.0,
        "fiber": 5.0
    }
}
```

## Configuration

Variables d'environnement requises dans `.env` :
- `GOOGLE_API_KEY` ou `API_KEY` : Clé API Google Gemini
- `WEEKLY_SCORE_SYSTEM_PROMPT` (optionnel) : Prompt personnalisé

## Exemple de réponse

```json
{
  "score": 4.2,
  "comment": "Excellente variété cette semaine ! Continue à intégrer des légumes et des protéines."
}
```
