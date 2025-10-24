"""
Module AI pour les fonctionnalités d'intelligence artificielle
Contient les agents d'analyse et de suggestions avec Gemini
"""

from .agents.agent_meal_suggestion import MealSuggestionAgent
from .agents.agent_onboarding import OnboardingAgent
from .agents.agent_coach import CoachAgent
from .agents.agent_orchestrator import OrchestratorAgent
from .agents.agent_initializer import (
    get_food_analyzer,
    get_nutrient_analyzer,
    get_meal_suggestion_agent,
    get_onboarding_agent,
    get_coach_agent,
    get_orchestrator_agent
)

__all__ = [
    'MealSuggestionAgent',
    'OnboardingAgent',
    'CoachAgent',
    'OrchestratorAgent',
    'get_food_analyzer',
    'get_nutrient_analyzer',
    'get_meal_suggestion_agent',
    'get_onboarding_agent',
    'get_coach_agent',
    'get_orchestrator_agent'
]
