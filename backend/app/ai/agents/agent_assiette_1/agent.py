"""
Agent for analyzing macro-nutrients and micro-nutrients based on a list of aliments via Vertex AI.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path
from vertexai.generative_models import GenerativeModel
import vertexai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NutrientAnalyzerAgent:
    """
    Agent to calculate macro-nutrients and micro-nutrients for a list of aliments.
    """

    PROMPT_TEMPLATE = """
    You are a nutrition expert. Analyze the following list of foods and return complete nutritional values for each food item.

    List of detected foods:
    {aliments_json}

    For each food item, return a JSON with the following nutritional information:
    - Values for the indicated quantity (per portion)
    - Macronutrients: calories, proteins, carbohydrates, lipids, fiber, sugars, saturated fats, unsaturated fats
    - Main micronutrients: calcium, iron, magnesium, potassium, sodium, zinc, phosphorus

    JSON structure to return (WITHOUT markdown tags):

    {{
    "foods_nutrition": [
        {{
        "food": "food name",
        "quantity": quantity_integer,
        "per_portion": {{
            "nutritional_values": {{
            "energy_kcal": number,
            "proteins_g": number,
            "carbohydrates_g": number,
            "lipids_g": number,
            "fiber_g": number,
            "sugars_g": number,
            "saturated_fats_g": number,
            "unsaturated_fats_g": number
            }},
            "micronutrients": {{
            "calcium_mg": number,
            "iron_mg": number,
            "magnesium_mg": number,
            "potassium_mg": number,
            "sodium_mg": number,
            "zinc_mg": number,
            "phosphorus_mg": number
            }}
        }}
        }}
    ]
    }}

    Use standard average nutritional values from reliable nutritional databases. If a food can vary depending on preparation method (grilled, boiled, raw, etc.), use the most common preparation method.

    IMPORTANT:
    - All numbers must be numeric values (not strings)
    - "quantity" must be an integer representing grams
    - All micronutrient field names must be in English: use "iron_mg" not "fer_mg", "phosphorus_mg" not "phosphore_mg"
    - Return ONLY the JSON, with no text before or after, and no markdown tags
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-001",
        load_env: bool = True
    ):
        """
        Initialize the NutrientAnalyzerAgent.
        
        Args:
            project_id: Google Cloud Project ID
            location: Google Cloud Location (e.g., 'europe-west4')
            model_name: Nom du modèle Gemini à utiliser
            load_env: Si True, charge les variables d'environnement depuis .env
        """
        if load_env:
            # Remonter 6 niveaux pour atteindre la racine du projet
            # agent.py -> agent_assiette_1 -> agents -> ai -> app -> backend -> PROJECT_ROOT
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        # Configuration Vertex AI
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.location = location or os.getenv('GCP_LOCATION', 'us-central1')
        
        if not self.project_id:
            raise ValueError(
                "GCP_PROJECT_ID manquant. "
                "Définissez GCP_PROJECT_ID dans .env"
            )
        
        # Initialiser Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model_name = model_name
        self.model = GenerativeModel(model_name)
        
        logger.info(f"NutrientAnalyzerAgent initialisé avec le modèle {model_name} sur Vertex AI")
        logger.info(f"Project: {self.project_id}, Location: {self.location}")

    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse la réponse JSON du modèle.
        
        Args:
            response_text: Texte brut de la réponse
            
        Returns:
            Dictionnaire Python parsé
        """
        try:
            # Nettoie les balises markdown si présentes
            response_text = response_text.strip()
            
            # Enlève les ```json et ``` si présents
            if response_text.startswith('```'):
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    response_text = response_text[start:end]
            
            # Parse le JSON
            result = json.loads(response_text)
            logger.info("Réponse JSON parsée avec succès")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            logger.error(f"Réponse brute: {response_text}")
            raise ValueError(f"Impossible de parser la réponse JSON: {e}")

    def analyze_nutrients(self, aliments: List[Dict]) -> Dict:
        """
        Analyze the macro-nutrients and micro-nutrients for each aliment using the Google API.

        Args:
            aliments: A list of dictionaries, each containing 'nom' and 'quantite_estimee'.

        Returns:
            A dictionary containing detailed nutrient information.
        """
        logger.info(f"Analyse nutritionnelle de {len(aliments)} aliments...")
        
        # Convertit la liste d'aliments en JSON
        aliments_json = json.dumps(aliments, indent=2, ensure_ascii=False)
        
        # Formate le prompt
        prompt = self.PROMPT_TEMPLATE.format(aliments_json=aliments_json)
        
        
        try:
            # Appel à Vertex AI Gemini
            print("Appel à Vertex AI Gemini...")
            response_text = self._call_gemini_text(prompt)
            
            # Parse la réponse
            result = self._parse_response(response_text)
            
            logger.info("Analyse nutritionnelle terminée avec succès")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}")
            print(f"Erreur: Impossible de décoder la réponse JSON de l'API.")
            raise ValueError("Failed to decode the JSON response from the API.")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse nutritionnelle: {e}")
            print(f"Erreur: {e}")
            raise RuntimeError(f"An error occurred while analyzing nutrients: {e}")
    
    def _call_gemini_text(self, prompt: str) -> str:
        """
        Appelle Vertex AI Gemini avec un prompt texte.
        
        Args:
            prompt: Le prompt à envoyer
            
        Returns:
            La réponse de l'IA
        """
        try:
            logger.debug(f"Appel Vertex AI Gemini")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.4,
                    "max_output_tokens": 4096,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )
            
            text = response.text.strip()
            logger.debug(f"Réponse Vertex AI: {text[:100]}...")
            
            return text
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à Vertex AI: {e}")
            raise Exception(f"Erreur Vertex AI: {str(e)}")

    def format_results(self, result: Dict) -> str:
        """
        Formate les résultats pour un affichage lisible.
        
        Args:
            result: Résultat de l'analyse nutritionnelle
            
        Returns:
            Chaîne formatée
        """
        output = ["=== Analyse Nutritionnelle ===\n"]
        
        for aliment_data in result.get('aliments_nutrition', []):
            aliment = aliment_data.get('aliment', 'Inconnu')
            quantite = aliment_data.get('quantite', 0)
            
            output.append(f"\n {aliment} ({quantite}g)")
            output.append("-" * 50)
            
            # Valeurs pour la portion
            portion = aliment_data.get('valeurs_nutritionnelles', {}).get('pour_portion', {})
            output.append(f"  Énergie: {portion.get('energie_kcal', 0)} kcal")
            output.append(f"  Protéines: {portion.get('proteines_g', 0)}g")
            output.append(f"  Glucides: {portion.get('glucides_g', 0)}g")
            output.append(f"  Lipides: {portion.get('lipides_g', 0)}g")
            output.append(f"  Fibres: {portion.get('fibres_g', 0)}g")
            
            # Micronutriments
            micro = aliment_data.get('valeurs_nutritionnelles', {}).get('micronutriments', {})
            if micro:
                output.append("\n  Micronutriments principaux:")
                output.append(f"    Calcium: {micro.get('calcium_mg', 0)}mg")
                output.append(f"    Fer: {micro.get('fer_mg', 0)}mg")
                output.append(f"    Magnésium: {micro.get('magnesium_mg', 0)}mg")
            
            # Notes
            notes = aliment_data.get('notes', '')
            if notes:
                output.append(f"\n  Notes: {notes}")
            
            output.append("")
        
        return "\n".join(output)


# Isolated testing
if __name__ == "__main__":
    print("=" * 60)
    print("Testing NutrientAnalyzerAgent with sample data...")
    print("=" * 60)
    
    try:
        agent = NutrientAnalyzerAgent()
        print(" NutrientAnalyzerAgent instance created.\n")
        
        sample_aliments = [
            {"nom": "Pomme", "quantite_estimee": 150},
            {"nom": "Poulet grillé", "quantite_estimee": 200}
        ]
        
        print("Sample aliments prepared for analysis:")
        print(json.dumps(sample_aliments, indent=2, ensure_ascii=False))
        print("\n" + "=" * 60)
        
        analysis = agent.analyze_nutrients(sample_aliments)
        
        print("\n" + "=" * 60)
        print("RÉSULTATS DE L'ANALYSE")
        print("=" * 60)
        print(agent.format_results(analysis))
        
        print("\n" + "=" * 60)
        print("JSON COMPLET:")
        print("=" * 60)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()