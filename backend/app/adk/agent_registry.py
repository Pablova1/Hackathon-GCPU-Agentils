"""
ADK Agent Registry - Centralized agent management
"""
import logging
from typing import Optional
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

# Singleton instances
_coach_agent: Optional[Agent] = None
_meal_agent: Optional[Agent] = None
_meal_coach_agent: Optional[Agent] = None
_medical_agent: Optional[Agent] = None

# PlateAnalyzerAgent singleton
_plate_analyzer_agent: Optional[Agent] = None

def get_plate_analyzer_agent() -> Agent:
    """Get or create PlateAnalyzerAgent singleton"""
    global _plate_analyzer_agent
    if _plate_analyzer_agent is None:
        from app.adk.image_agent.plate_analyze.agent import root_agent
        _plate_analyzer_agent = root_agent
        logger.info("PlateAnalyzerAgent (ADK) initialized")
    return _plate_analyzer_agent


# NutrimentAnalyzerAgent singleton
_nutriment_analyzer_agent: Optional[Agent] = None

def get_nutriment_analyzer_agent() -> Agent:  
    """Get or create NutrimentAnalyzerAgent singleton"""
    global _nutriment_analyzer_agent
    if _nutriment_analyzer_agent is None:
        from app.adk.image_agent.nutriment_analyze.agent import root_agent
        _nutriment_analyzer_agent = root_agent
        logger.info("NutrimentAnalyzerAgent (ADK) initialized")
    return _nutriment_analyzer_agent


def get_coach_agent() -> Agent:
    """Get or create CoachAgent singleton"""
    global _coach_agent
    if _coach_agent is None:
        from app.adk.suggestions.coach_agent.agent import root_agent
        _coach_agent = root_agent
        logger.info("CoachAgent (ADK) initialized")
    return _coach_agent


def get_meal_agent() -> Agent:
    """Get or create MealAgent singleton"""
    global _meal_agent
    if _meal_agent is None:
        from app.adk.suggestions.meal_agent.agent import root_agent
        _meal_agent = root_agent
        logger.info("MealAgent (ADK) initialized")
    return _meal_agent


def get_meal_coach_agent() -> Agent:
    """Get or create MealCoachAgent singleton"""
    global _meal_coach_agent
    if _meal_coach_agent is None:
        from app.adk.suggestions.meal_coach.agent import root_agent
        _meal_coach_agent = root_agent
        logger.info("MealCoachAgent (ADK) initialized")
    return _meal_coach_agent


def get_medical_agent() -> Agent:
    """Get or create MedicalAgent singleton"""
    global _medical_agent
    if _medical_agent is None:
        from app.adk.suggestions.medical_agent.agent import root_agent
        _medical_agent = root_agent
        logger.info("MedicalAgent (ADK) initialized")
    return _medical_agent