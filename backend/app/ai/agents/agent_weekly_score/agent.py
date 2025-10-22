"""
Agent pour calculer une note hebdomadaire basée sur l'alimentation.

Cet agent analyse les repas scannés durant les 7 derniers jours
et génère une note de 1 à 5 avec un commentaire encourageant.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeeklyScoreAgent:
    """
    Agent pour calculer une note hebdomadaire (1-5) basée sur les repas.
    
    Utilise Google Gemini pour analyser la qualité nutritionnelle
    des repas de la semaine et fournir un feedback encourageant.
    """
    
    DEFAULT_SYSTEM_PROMPT = """Tu es un nutritionniste IA bienveillant et encourageant.

Voici les repas scannés par l'utilisateur durant les 7 derniers jours :

{meals_summary}

Ta mission :
1. Analyse la qualité nutritionnelle globale de ces repas
2. Donne une note de 1 à 5 (1 = très mauvais, 5 = excellent)
3. Écris un commentaire COURT et ENCOURAGEANT (maximum 2 phrases)

Critères d'évaluation :
- Variété des aliments
- Équilibre nutritionnel (protéines, glucides, lipides, fibres)
- Présence de fruits et légumes
- Quantités raisonnables

IMPORTANT : Retourne UNIQUEMENT un JSON valide avec cette structure :
{
  "score": 4.5,
  "comment": "Excellente variété cette semaine ! Continue à intégrer des légumes."
}

Ne retourne RIEN d'autre que ce JSON, pas de texte avant ou après."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        system_prompt: Optional[str] = None,
        load_env: bool = True
    ):
        """
        Initialise l'agent de notation hebdomadaire.
        
        Args:
            api_key: Clé API Google Cloud (si None, charge depuis .env)
            project_id: ID du projet GCP (si None, charge depuis .env)
            region: Région GCP (si None, charge depuis .env)
            system_prompt: Prompt système personnalisé
            load_env: Si True, charge les variables d'environnement depuis .env
        """
        if load_env:
            # Remonter 6 niveaux pour atteindre la racine du projet
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
            logger.debug(f"Chargement du .env depuis: {env_path}")
            load_dotenv(dotenv_path=env_path, override=True)
        
        # Récupération des variables d'environnement
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        self.region = region or os.getenv('GCP_REGION') or os.getenv('REGION', 'us-central1')
        self.system_prompt = system_prompt or os.getenv('WEEKLY_SCORE_SYSTEM_PROMPT') or self.DEFAULT_SYSTEM_PROMPT
        
        if not self.api_key:
            raise ValueError(
                "Clé API manquante. Définis GOOGLE_API_KEY ou API_KEY dans .env "
                "ou passe-la en paramètre."
            )
        
        logger.info("Agent WeeklyScore initialisé")
    
    def calculate_score(self, meals: List[Dict]) -> Optional[Dict]:
        """
        Calcule une note hebdomadaire basée sur les repas.
        
        Args:
            meals: Liste des repas de la semaine avec leurs informations
            
        Returns:
            Dictionnaire avec score (1-5) et commentaire, ou None en cas d'erreur
            Format: {"score": 4.0, "comment": "Excellente semaine !"}
        """
        # Cas spécial : aucun repas
        if not meals:
            logger.info("Aucun repas scanné cette semaine")
            return {
                "score": 1.0,
                "comment": "Aucun repas scanné cette semaine. Commence à scanner tes plats pour suivre ton alimentation !"
            }
        
        # Préparer le résumé des repas
        meals_summary = self._format_meals_summary(meals)
        
        # Générer le prompt
        prompt = self.system_prompt.format(meals_summary=meals_summary)
        
        # Appeler l'IA
        try:
            response_text = self._call_gemini_api(prompt)
            
            if not response_text:
                logger.error("Aucune réponse de l'API")
                return None
            
            # Parser la réponse JSON
            result = self._parse_response(response_text)
            
            logger.info(f"Score calculé: {result['score']}/5")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score: {e}", exc_info=True)
            return None
    
    def _format_meals_summary(self, meals: List[Dict]) -> str:
        """
        Formate les repas en texte lisible pour l'IA.
        
        Args:
            meals: Liste des repas
            
        Returns:
            Texte formaté décrivant les repas
        """
        summary_lines = []
        
        for i, meal in enumerate(meals, 1):
            nutrients = meal.get("nutrients", {})
            ingredients = meal.get("ingredients", [])
            
            meal_info = f"Repas {i}: {meal.get('name', 'Sans nom')}"
            
            if ingredients:
                # Limiter à 5 ingrédients pour ne pas surcharger
                ingredients_str = ", ".join(ingredients[:5])
                if len(ingredients) > 5:
                    ingredients_str += f" (+ {len(ingredients) - 5} autres)"
                meal_info += f"\n  Ingrédients: {ingredients_str}"
            
            if nutrients:
                meal_info += f"\n  Calories: {nutrients.get('calories', 'N/A')} kcal"
                meal_info += f", Protéines: {nutrients.get('protein', 'N/A')}g"
                meal_info += f", Glucides: {nutrients.get('carbohydrates', 'N/A')}g"
                meal_info += f", Lipides: {nutrients.get('fat', 'N/A')}g"
                if nutrients.get('fiber'):
                    meal_info += f", Fibres: {nutrients.get('fiber')}g"
            
            summary_lines.append(meal_info)
        
        return "\n\n".join(summary_lines)
    
    def _call_gemini_api(self, prompt: str, timeout: int = 20) -> Optional[str]:
        """
        Appelle l'API Google Gemini.
        
        Args:
            prompt: Le prompt à envoyer
            timeout: Timeout de la requête en secondes
            
        Returns:
            La réponse de l'IA ou None en cas d'erreur
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200,
                "topP": 0.9,
                "topK": 40
            }
        }
        
        try:
            logger.debug(f"Appel API Gemini")
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            logger.debug(f"Réponse reçue: {text[:100]}...")
            return text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout lors de l'appel à l'API Gemini (>{timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur HTTP: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Format de réponse inattendu: {e}")
            logger.debug(f"Données reçues: {data if 'data' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}", exc_info=True)
            return None
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse la réponse JSON de l'IA.
        
        Args:
            response_text: Texte brut de la réponse
            
        Returns:
            Dictionnaire avec score et commentaire
            
        Raises:
            ValueError: Si le parsing échoue ou si le format est invalide
        """
        try:
            # Nettoyer le texte (enlever les balises markdown si présentes)
            text = response_text.strip()
            
            # Enlever les blocs de code markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Extraire le JSON même s'il y a du texte avant/après
            # Chercher le premier { et le dernier }
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise ValueError(f"Pas de JSON trouvé dans: {text}")
            
            json_text = text[start_idx:end_idx+1]
            
            # Parser le JSON
            result = json.loads(json_text)
            
            # Valider le score
            score = result.get("score")
            if not isinstance(score, (int, float)):
                raise ValueError(f"Score invalide: {score} (doit être un nombre)")
            
            if score < 1 or score > 5:
                raise ValueError(f"Score hors limites: {score} (doit être entre 1 et 5)")
            
            # Valider le commentaire
            comment = result.get("comment")
            if not isinstance(comment, str) or not comment.strip():
                raise ValueError("Commentaire manquant ou invalide")
            
            return {
                "score": float(score),
                "comment": comment.strip()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            logger.error(f"Texte reçu: {response_text}")
            raise ValueError(f"Impossible de parser la réponse JSON: {e}")
        except ValueError as e:
            logger.error(f"Validation échouée: {e}")
            raise


# Point d'entrée pour tests
if __name__ == "__main__":
    # Exemple de test
    agent = WeeklyScoreAgent()
    
    # Données de test
    test_meals = [
        {
            "name": "Poulet grillé avec riz",
            "ingredients": ["poulet", "riz", "brocoli"],
            "nutrients": {
                "calories": 450,
                "protein": 35,
                "carbohydrates": 45,
                "fat": 12,
                "fiber": 5
            }
        },
        {
            "name": "Salade César",
            "ingredients": ["laitue", "poulet", "parmesan", "croûtons"],
            "nutrients": {
                "calories": 350,
                "protein": 28,
                "carbohydrates": 20,
                "fat": 18,
                "fiber": 3
            }
        }
    ]
    
    result = agent.calculate_score(test_meals)
    print(f"\nScore: {result['score']}/5")
    print(f"Commentaire: {result['comment']}")
