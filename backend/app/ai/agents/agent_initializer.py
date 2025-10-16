"""
Module to initialize and manage the FoodAnalyzerAgent instance.
"""

from app.core.config import settings
from app.ai.agents.agent_assiette_0.agent import FoodAnalyzerAgent
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Singleton instance of FoodAnalyzerAgent
_food_analyzer = None

def get_analyzer() -> FoodAnalyzerAgent:
    """Retrieve or create the singleton instance of FoodAnalyzerAgent."""
    global _food_analyzer
    if _food_analyzer is None:
        try:
            _food_analyzer = FoodAnalyzerAgent(
                model_name=settings.GEMINI_MODEL
            )
            logger.info("Agent d'analyse initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation agent: {e}")
            raise HTTPException(
                status_code=503,
                detail="Impossible d'initialiser l'agent d'analyse"
            )
    return _food_analyzer