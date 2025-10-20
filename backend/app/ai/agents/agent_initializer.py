"""
Module to initialize and manage agent instances.
"""
from app.core.config import settings
from app.ai.agents.agent_assiette_0.agent import FoodAnalyzerAgent
from app.ai.agents.agent_assiette_1.agent import NutrientAnalyzerAgent
from app.ai.agents.agent_onboarding.agent import OnboardingAgent
from app.ai.agents.agent_meal_suggestion.agent import MealSuggestionAgent
from app.ai.agents.agent_coach.agent import CoachAgent
from app.ai.agents.agent_orchestrator.agent import OrchestratorAgent
from app.db.mongo_client import db
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Singleton instances
_food_analyzer = None
_nutrient_analyzer = None
_onboarding_agent = None
_meal_suggestion_agent = None
_coach_agent = None
_orchestrator_agent = None


def get_food_analyzer() -> FoodAnalyzerAgent:
    """Retrieve or create the singleton instance of FoodAnalyzerAgent."""
    global _food_analyzer
    if _food_analyzer is None:
        try:
            _food_analyzer = FoodAnalyzerAgent(
                model_name=settings.GEMINI_MODEL
            )
            logger.info("FoodAnalyzerAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation FoodAnalyzerAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail="Impossible d'initialiser l'agent d'analyse d'image"
            )
    return _food_analyzer


def get_nutrient_analyzer() -> NutrientAnalyzerAgent:
    """Retrieve or create the singleton instance of NutrientAnalyzerAgent."""
    global _nutrient_analyzer
    if _nutrient_analyzer is None:
        try:
            _nutrient_analyzer = NutrientAnalyzerAgent(
                model_name=settings.GEMINI_MODEL
            )
            logger.info("NutrientAnalyzerAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation NutrientAnalyzerAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail="Impossible d'initialiser l'agent d'analyse nutritionnelle"
            )
    return _nutrient_analyzer


def get_onboarding_agent() -> OnboardingAgent:
    """Retrieve or create the singleton instance of OnboardingAgent."""
    global _onboarding_agent
    if _onboarding_agent is None:
        try:
            _onboarding_agent = OnboardingAgent()
            logger.info("OnboardingAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation OnboardingAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail="Impossible d'initialiser l'agent d'onboarding"
            )
    return _onboarding_agent


def get_meal_suggestion_agent() -> MealSuggestionAgent:
    """Retrieve or create the singleton instance of MealSuggestionAgent."""
    global _meal_suggestion_agent
    if _meal_suggestion_agent is None:
        try:
            # Utiliser directement l'instance db asynchrone
            _meal_suggestion_agent = MealSuggestionAgent(
                mongo_db=db,
                model_name=settings.GEMINI_MODEL
            )
            logger.info("MealSuggestionAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation MealSuggestionAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Impossible d'initialiser l'agent de suggestion de repas: {str(e)}"
            )
    return _meal_suggestion_agent


def get_coach_agent() -> CoachAgent:
    """Retrieve or create the singleton instance of CoachAgent."""
    global _coach_agent
    if _coach_agent is None:
        try:
            _coach_agent = CoachAgent(
                mongo_db=db,
                model_name=settings.GEMINI_MODEL
            )
            logger.info("CoachAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation CoachAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Impossible d'initialiser l'agent coach: {str(e)}"
            )
    return _coach_agent


def get_orchestrator_agent() -> OrchestratorAgent:
    """Retrieve or create the singleton instance of OrchestratorAgent."""
    global _orchestrator_agent
    if _orchestrator_agent is None:
        try:
            _orchestrator_agent = OrchestratorAgent(
                model_name=settings.GEMINI_MODEL
            )
            logger.info("OrchestratorAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation OrchestratorAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Impossible d'initialiser l'agent orchestrateur: {str(e)}"
            )
    return _orchestrator_agent
