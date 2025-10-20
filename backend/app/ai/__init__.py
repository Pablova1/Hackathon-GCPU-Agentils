"""
Module AI pour les fonctionnalités d'intelligence artificielle
Contient les agents d'analyse et de suggestions avec Gemini
"""

from .agents.agent_meal_suggestion import MealSuggestionAgent
from .agents.agent_onboarding import OnboardingAgent
from .agents.agent_initializer import (
    get_food_analyzer,
    get_nutrient_analyzer,
    get_meal_suggestion_agent,
    get_onboarding_agent
)

__all__ = [
    'MealSuggestionAgent',
    'OnboardingAgent',
    'get_food_analyzer',
    'get_nutrient_analyzer',
    'get_meal_suggestion_agent',
    'get_onboarding_agent'
]
