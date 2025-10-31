"""
Agent d'onboarding pour générer des questions IA personnalisées.

Cet agent analyse les réponses de l'utilisateur aux questions obligatoires
et génère des questions de suivi pertinentes pour enrichir son profil.
"""

import os
import logging
import requests
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OnboardingAgent:
    """
    Agent pour générer des questions personnalisées pendant l'onboarding.
    
    Utilise Google Gemini via Vertex AI pour analyser le contexte utilisateur
    et suggérer des questions de suivi pertinentes.
    """
    
    DEFAULT_SYSTEM_PROMPT = """Tu es un assistant nutritionniste bienveillant qui pose des questions pour mieux connaître l'utilisateur.
    Voici le contexte actuel de l'utilisateur :
    
    {context}
    
    Sur la base de ces informations, pose UNE question ouverte et pertinente pour mieux comprendre ses habitudes alimentaires, 
    ses préférences ou ses objectifs de santé. 
    
    IMPORTANT:
    - Pose SEULEMENT UNE question courte et claire
    - Ne réponds pas "AUCUNE" sauf si vraiment rien de pertinent à demander
    - La question doit être en lien avec la nutrition, la santé ou le bien-être
    - Sois naturel et conversationnel
    
    Ta question :"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_questions: int = 3,
        load_env: bool = True
    ):
        """
        Initialise l'agent d'onboarding.
        
        Args:
            api_key: Clé API Google Cloud (si None, charge depuis .env)
            project_id: ID du projet GCP (si None, charge depuis .env)
            region: Région GCP (si None, charge depuis .env)
            system_prompt: Prompt système personnalisé
            max_questions: Nombre maximum de questions IA à poser
            load_env: Si True, charge les variables d'environnement depuis .env
        """
        if load_env:
            # Remonter 6 niveaux pour atteindre la racine du projet
            # agent.py -> agent_onboarding -> agents -> ai -> app -> backend -> PROJECT_ROOT
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
            logger.debug(f"Chargement du .env depuis: {env_path}")
            logger.debug(f"Fichier existe: {env_path.exists()}")
            load_dotenv(dotenv_path=env_path, override=True)
        
        # Récupération des variables d'environnement
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        self.region = region or os.getenv('GCP_REGION') or os.getenv('REGION', 'us-central1')
        self.system_prompt = system_prompt or os.getenv('AI_SYSTEM_PROMPT') or self.DEFAULT_SYSTEM_PROMPT
        self.max_questions = max_questions
        
        logger.debug(f"API Key chargée: {bool(self.api_key)}")
        logger.debug(f"Project ID: {self.project_id}")
        logger.debug(f"Region: {self.region}")
        
        if not self.api_key:
            raise ValueError(
                "Clé API manquante. Définis GOOGLE_API_KEY ou API_KEY dans .env "
                "ou passe-la en paramètre."
            )
        
        if not self.project_id:
            logger.warning("PROJECT_ID non défini. Certaines fonctionnalités peuvent être limitées.")
        
        logger.info(f"Agent Onboarding initialisé (max_questions={self.max_questions})")
    
    def suggest_followup(self, slots: Dict[str, any], asked_ai_count: int) -> Optional[Dict]:
        """
        Suggère une question IA de suivi basée sur le contexte utilisateur.
        
        Args:
            slots: Dictionnaire des réponses déjà fournies par l'utilisateur
            asked_ai_count: Nombre de questions IA déjà posées
            
        Returns:
            Dictionnaire avec la question suggérée ou None si aucune question
        """
        # Vérifier si on a atteint le maximum de questions
        if asked_ai_count >= self.max_questions:
            logger.info(f"Maximum de questions IA atteint ({self.max_questions})")
            return None
        
        # Construire le contexte à partir des slots
        context_lines = [f"{k}: {v}" for k, v in slots.items() if v]
        context_text = "\n".join(context_lines) or "Aucun contexte fourni."
        
        # Générer le prompt avec le contexte
        prompt = self.system_prompt.format(context=context_text)
        
        # Appeler l'API Gemini
        try:
            question_text = self._call_gemini_api(prompt)
            
            if not question_text:
                logger.info("Aucune question suggérée par l'IA")
                return None
            
            # Vérifier si l'IA a répondu "AUCUNE"
            if question_text.upper().startswith("AUCUNE"):
                logger.info("L'IA a décidé de ne pas poser de question supplémentaire")
                return None
            
            # Créer l'objet question
            question = {
                "slot": f"ai_followup_{asked_ai_count}",
                "text": question_text,
                "type": "text",
                "source": "ai"
            }
            
            logger.info(f"Question IA générée: {question_text[:50]}...")
            return question
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de question IA: {e}", exc_info=True)
            return None
    
    def _call_gemini_api(self, prompt: str, timeout: int = 20) -> Optional[str]:
        """
        Appelle l'API Google Gemini (generativelanguage).
        
        Args:
            prompt: Le prompt à envoyer à l'API
            timeout: Timeout de la requête en secondes
            
        Returns:
            La réponse de l'IA ou None en cas d'erreur
        """
        # Utiliser l'API Google AI (generativelanguage) au lieu de Vertex AI
        # Cette API fonctionne avec juste une clé API, sans OAuth2
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
            logger.debug(f"Appel API Gemini: {url}")
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraire le texte de la réponse
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            logger.debug(f"Réponse API: {text[:100]}...")
            
            return text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout lors de l'appel à l'API Gemini (>{timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur HTTP lors de l'appel à l'API Gemini: {e}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Format de réponse inattendu de l'API Gemini: {e}")
            logger.debug(f"Données reçues: {data}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'appel à l'API: {e}", exc_info=True)
            return None


# Instance globale pour compatibilité avec l'ancien code
_default_agent = None

def get_default_agent() -> OnboardingAgent:
    """Retourne une instance par défaut de l'agent."""
    global _default_agent
    if _default_agent is None:
        _default_agent = OnboardingAgent()
    return _default_agent


def suggest_followup(slots: dict, asked_ai_count: int) -> dict | None:
    """
    Fonction de compatibilité avec l'ancienne API.
    Utilise l'agent par défaut pour suggérer une question.
    """
    agent = get_default_agent()
    return agent.suggest_followup(slots, asked_ai_count)
