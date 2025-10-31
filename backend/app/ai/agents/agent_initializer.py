"""
Module to initialize and manage agent instances.
"""
from app.core.config import settings
from app.ai.agents.agent_onboarding.agent import OnboardingAgent
from app.db.mongo_client import db
from app.ai.agents.agent_weekly_score.agent import WeeklyScoreAgent
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


_onboarding_agent = None
_weekly_score_agent = None

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

def get_weekly_score_agent() -> WeeklyScoreAgent:
    """Retrieve or create the singleton instance of WeeklyScoreAgent."""
    global _weekly_score_agent
    if _weekly_score_agent is None:
        try:
            _weekly_score_agent = WeeklyScoreAgent()
            logger.info("WeeklyScoreAgent initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation WeeklyScoreAgent: {e}")
            raise HTTPException(
                status_code=503,
                detail="Impossible d'initialiser l'agent de notation hebdomadaire"
            )
    return _weekly_score_agent

