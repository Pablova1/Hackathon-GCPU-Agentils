"""
Module to initialize and manage agent instances.
"""
from app.core.config import settings
from app.ai.agents.agent_assiette_0.agent import FoodAnalyzerAgent
from app.ai.agents.agent_assiette_1.agent import NutrientAnalyzerAgent
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Singleton instances
_food_analyzer = None
_nutrient_analyzer = None


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


