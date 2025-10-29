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
            logger.info(f"Loading .env from: {env_path}")
            logger.info(f"File exists: {env_path.exists()}")
            if env_path.exists():
                load_dotenv(dotenv_path=env_path, override=True)
                logger.info(".env file loaded successfully")
            else:
                logger.warning(f".env file not found at {env_path}")
                # Try also in backend folder
                backend_env = Path(__file__).parent.parent.parent.parent.parent / ".env"
                logger.info(f"Trying backend .env: {backend_env}")
                if backend_env.exists():
                    load_dotenv(dotenv_path=backend_env, override=True)
                    logger.info("Loaded .env from backend folder")
                else:
                    logger.warning("No .env file found")
        
        # Récupération des variables d'environnement
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID') or os.getenv('PROJECT_ID')
        self.region = region or os.getenv('GCP_REGION') or os.getenv('REGION', 'us-central1')
        
        # Charger le system prompt avec un fallback
        self.system_prompt = system_prompt or os.getenv('AI_SYSTEM_PROMPT')
        if not self.system_prompt:
            logger.warning("AI_SYSTEM_PROMPT not found in .env, using default prompt")
            self.system_prompt = (
                "You are a caring nutrition assistant who asks questions to get to know the user better. "
                "Here is the user's current context: {context}. "
                "Based on this information, ask ONE open-ended, relevant question to better understand "
                "their eating habits, preferences, or health goals. "
                "IMPORTANT: Ask ONLY ONE short, clear question. Do not answer 'NONE' unless there is truly nothing relevant to ask. "
                "The question must be related to nutrition, health, or wellness. Be natural and conversational."
            )
        
        self.max_questions = max_questions
        
        logger.info(f"API Key loaded: {bool(self.api_key)}")
        logger.info(f"Project ID: {self.project_id}")
        logger.info(f"Region: {self.region}")
        logger.info(f"System Prompt loaded: {bool(self.system_prompt)}")
        logger.debug(f"System Prompt preview: {self.system_prompt[:100]}...")
        
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
        Appelle l'API Vertex AI Gemini.
        
        Args:
            prompt: Le prompt à envoyer à l'API
            timeout: Timeout de la requête en secondes
            
        Returns:
            La réponse de l'IA ou None en cas d'erreur
        """
        # Utiliser Vertex AI
        try:
            from google.auth import default
            from google.auth.transport.requests import Request
            
            # Obtenir les credentials par défaut (utilise GOOGLE_APPLICATION_CREDENTIALS ou gcloud auth)
            credentials, _ = default()
            
            # Rafraîchir le token si nécessaire
            if not credentials.valid:
                credentials.refresh(Request())
            
            # Construire l'URL Vertex AI
            model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-001')
            url = f"https://{self.region}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{model}:generateContent"
            
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
            
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Appel API Vertex AI: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraire le texte de la réponse
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            logger.debug(f"Réponse API: {text[:100]}...")
            
            return text
            
        except ImportError:
            logger.error("Bibliothèque google-auth non installée. Installez-la avec: pip install google-auth")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout lors de l'appel à l'API Vertex AI (>{timeout}s)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur HTTP lors de l'appel à l'API Vertex AI: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse: {e.response.text}")
            return None
        except (KeyError, IndexError) as e:
            logger.error(f"Format de réponse inattendu de l'API Vertex AI: {e}")
            logger.debug(f"Données reçues: {data if 'data' in locals() else 'N/A'}")
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
