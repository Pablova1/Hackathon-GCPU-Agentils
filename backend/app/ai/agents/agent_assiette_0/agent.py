"""
Agent d'analyse de composition d'assiettes utilisant Google Gemini.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FoodAnalyzerAgent:
    """
    Agent pour analyser la composition d'une assiette à partir d'une image.
    """
    
    PROMPT_TEMPLATE = """
    Analyse cette photo d'assiette et identifie tous les aliments présents.
    Retourne UNIQUEMENT un JSON valide avec cette structure exacte :
    {
      "aliments": [
        {
          "nom": "nom de l'aliment",
          "quantite_estimee": "quantité en grammes"
        }
      ]
    }
    Ne retourne rien d'autre que le JSON, pas de texte avant ou après.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        load_env: bool = True
    ):
        """
        Initialise l'agent d'analyse alimentaire.
        
        Args:
            api_key: Clé API Google Gemini (si None, charge depuis .env)
            model_name: Nom du modèle Gemini à utiliser
            load_env: Si True, charge les variables d'environnement depuis .env
        """
        if load_env:
            load_dotenv()
        
        # Récupère la clé API
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Clé API manquante. Définis GOOGLE_API_KEY dans .env "
                "ou passe api_key au constructeur."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"Agent initialisé avec le modèle {model_name}")
    
    def _load_image(self, image_path: Union[str, Path]) -> Image.Image:
        """
        Charge une image depuis un chemin.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Image PIL chargée
        """
        try:
            image = Image.open(image_path)
            logger.info(f"Image chargée: {image_path}")
            return image
        except Exception as e:
            logger.error(f"Erreur lors du chargement de l'image: {e}")
            raise
    
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
    
    def analyze_plate(
        self,
        image_path: Union[str, Path],
        custom_prompt: Optional[str] = None
    ) -> Dict:
        """
        Analyse une assiette et retourne sa composition.
        
        Args:
            image_path: Chemin vers l'image de l'assiette
            custom_prompt: Prompt personnalisé (optionnel)
            
        Returns:
            Dictionnaire contenant les aliments détectés
            
        Example:
            >>> agent = FoodAnalyzerAgent()
            >>> result = agent.analyze_plate("mon_assiette.jpg")
            >>> print(result['aliments'])
        """
        logger.info(f"Début de l'analyse de: {image_path}")
        
        # Charge l'image
        image = self._load_image(image_path)
        
        # Utilise le prompt personnalisé ou le prompt par défaut
        prompt = custom_prompt or self.PROMPT_TEMPLATE
        
        # Génère la réponse
        try:
            response = self.model.generate_content([prompt, image])
            logger.info("Réponse reçue du modèle")
            
            # Parse la réponse
            result = self._parse_response(response.text)
            
            # Log les résultats
            logger.info(f"Analyse terminée: {len(result.get('aliments', []))} aliments détectés")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            raise
    
    def get_food_list(self, image_path: Union[str, Path]) -> List[Dict]:
        """
        Retourne uniquement la liste des aliments détectés.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            Liste des aliments avec leurs informations
        """
        result = self.analyze_plate(image_path)
        return result.get('aliments', [])
    
    def format_results(self, result: Dict) -> str:
        """
        Formate les résultats pour un affichage lisible.
        
        Args:
            result: Résultat de l'analyse
            
        Returns:
            Chaîne formatée
        """
        output = ["Aliments détectés:"]
        for aliment in result.get('aliments', []):
            output.append(
                f"  - {aliment['nom']}: {aliment['quantite_estimee']}"
            )
        return "\n".join(output)




# Point d'entrée pour tests
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py <chemin_image>")
        sys.exit(1)
    
    # Crée l'agent
    agent = FoodAnalyzerAgent()
    
    # Analyse l'image
    image_path = sys.argv[1]
    result = agent.analyze_plate(image_path)
    
    # Affiche les résultats
    print("\n" + agent.format_results(result))
    
    # Affiche le JSON complet
    print("\nJSON complet:")
    print(json.dumps(result, indent=2, ensure_ascii=False))