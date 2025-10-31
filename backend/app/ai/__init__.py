"""
Module AI pour les fonctionnalités d'intelligence artificielle
Contient les agents d'analyse et de suggestions avec Gemini
"""

from .agents.agent_onboarding import OnboardingAgent
from .agents.agent_initializer import (
    get_onboarding_agent,
)

__all__ = [
    'OnboardingAgent',
    'get_onboarding_agent',
]
