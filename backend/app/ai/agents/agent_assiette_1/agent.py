"""
Agent for analyzing macro-nutrients and micro-nutrients based on a list of aliments via Google Gemini API.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

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
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-001",
        load_env: bool = False
    ):
        """
        Initialize the NutrientAnalyzerAgent with Google Gemini API.
        
        Args:
            api_key: Google API Key for Gemini
            model_name: Name of the Gemini model to use
            load_env: If True, loads environment variables from .env
        """
        if load_env:
            # Go up 6 levels to reach project root
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        # Get API key
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY missing. "
                "Set GOOGLE_API_KEY in .env or pass it as parameter"
            )
        
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        
        logger.info(f"NutrientAnalyzerAgent initialized with model {model_name}")

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Call Google Gemini API.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Model response text
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 8192,
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            
            logger.info("Response received from Gemini API")
            return response_text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise ValueError(f"Gemini API Error: {e}")

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
            aliments: A list of dictionaries, each containing 'name' and 'estimated_quantity'.

        Returns:
            A dictionary containing detailed nutrient information.
        """
        logger.info(f"Analyzing nutritional information for {len(aliments)} food items...")
        
        # Convert food list to JSON
        aliments_json = json.dumps(aliments, indent=2, ensure_ascii=False)
        
        # Format the prompt
        prompt = self.PROMPT_TEMPLATE.format(aliments_json=aliments_json)
        
        try:
            # Call Gemini API
            logger.info("Calling Gemini API...")
            response_text = self._call_gemini_api(prompt)
            
            # Parse the response
            result = self._parse_response(response_text)
            
            logger.info("Nutritional analysis completed successfully")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            print(f"Error: Unable to decode JSON response from the API.")
            raise ValueError("Failed to decode the JSON response from the API.")
        except Exception as e:
            logger.error(f"Error during nutritional analysis: {e}")
            print(f"Error: {e}")
            raise RuntimeError(f"An error occurred while analyzing nutrients: {e}")

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