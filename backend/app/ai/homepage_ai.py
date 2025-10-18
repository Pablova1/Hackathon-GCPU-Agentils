"""
Agent IA pour calculer une note hebdomadaire basée sur les plats scannés
"""
from dotenv import load_dotenv, find_dotenv
import os
import requests
from typing import List, Dict, Optional

load_dotenv(find_dotenv())
API_KEY: str | None = os.getenv("API_KEY")
PROJECT_ID: str | None = os.getenv("PROJECT_ID")
REGION: str = os.getenv("REGION")
WEEKLY_SCORE_SYSTEM_PROMPT: str | None = os.getenv("WEEKLY_SCORE_SYSTEM_PROMPT")


def calculate_weekly_score(meals: List[Dict]) -> Optional[Dict]:
    """
    Calcule une note hebdomadaire basée sur les plats scannés.
    
    Args:
        meals: Liste des repas de la semaine avec leurs informations nutritionnelles
        
    Returns:
        Dictionnaire avec la note (1-5) et un commentaire, ou None en cas d'erreur
        Format: {"score": 4, "comment": "Très bonne alimentation cette semaine !"}
    """
    if not meals:
        return {
            "score": 1,
            "comment": "Aucun repas scanné cette semaine. Commence à scanner tes plats pour suivre ton alimentation !"
        }
    
    # Préparer le résumé des repas pour l'IA
    meals_summary = []
    for i, meal in enumerate(meals, 1):
        nutrients = meal.get("nutrients", {})
        ingredients = meal.get("ingredients", [])
        
        meal_info = f"Repas {i}: {meal.get('name', 'Sans nom')}"
        if ingredients:
            meal_info += f"\n  Ingrédients: {', '.join(ingredients[:5])}"  # Limiter à 5 ingrédients
        if nutrients:
            meal_info += f"\n  Calories: {nutrients.get('calories', 'N/A')} kcal"
            meal_info += f"\n  Protéines: {nutrients.get('protein', 'N/A')}g"
            meal_info += f"\n  Glucides: {nutrients.get('carbohydrates', 'N/A')}g"
            meal_info += f"\n  Lipides: {nutrients.get('fat', 'N/A')}g"
            meal_info += f"\n  Fibres: {nutrients.get('fiber', 'N/A')}g"
        meals_summary.append(meal_info)
    
    context_text = "\n\n".join(meals_summary)
    
    prompt = f"""{WEEKLY_SCORE_SYSTEM_PROMPT}

Voici les {len(meals)} repas scannés cette semaine :

{context_text}

Analyse ces repas et donne une note de 1 à 5 avec un commentaire encourageant."""

    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 200
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"[WeeklyScoreAI] Erreur API: {e}")
        return None

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        print("[WeeklyScoreAI] Format de réponse inattendu:", data)
        return None
    
    # Parser la réponse JSON
    try:
        import json
        # Nettoyer le texte pour extraire le JSON (au cas où il y aurait du texte avant/après)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        
        # Valider le score
        score = result.get("score")
        if not isinstance(score, (int, float)) or score < 1 or score > 5:
            print(f"[WeeklyScoreAI] Score invalide: {score}")
            return None
        
        return {
            "score": float(score),
            "comment": result.get("comment", "Continue comme ça !")
        }
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[WeeklyScoreAI] Erreur de parsing JSON: {e}")
        print(f"[WeeklyScoreAI] Texte reçu: {text}")
        return None
