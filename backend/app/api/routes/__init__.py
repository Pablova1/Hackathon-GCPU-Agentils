"""
Initialisation des routes de l'API.

Ce fichier agrège tous les routers de l'application.
Tous les endpoints sont préfixés par /api dans main.py
"""

from fastapi import APIRouter
from .analyze import router as analyze_router
from .onboarding import router as onboarding_router
from .profile import router as profile_router
from .session import router as session_router
from .auth import router as auth_router
from .meal_suggestions import router as meal_suggestions_router
from .meal_router import router as meal_router
from .suggestions import router as suggestions_router
from .chatbot import router as chatbot_router
from .summary import router as summary_router

# Router principal qui agrège toutes les routes
api_router = APIRouter()

# Inclusion des sous-routes
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentification"]
)

api_router.include_router(
    analyze_router,
    prefix="/analyze",
    tags=["Analyse"]
)

api_router.include_router(
    onboarding_router,
    prefix="/onboarding",
    tags=["Onboarding"]
)

api_router.include_router(
    profile_router,
    prefix="/profile",
    tags=["Profil"]
)

api_router.include_router(
    session_router,
    prefix="/session",
    tags=["Sessions"]
)


api_router.include_router(
    meal_router,
    prefix="/meals",
    tags=["Meals"]
)

api_router.include_router(
    meal_suggestions_router,
    prefix="/meal-suggestions",
    tags=["Meal Suggestions"]
)

api_router.include_router(
    suggestions_router,
    prefix="/suggestions",
    tags=["Unified Suggestions"]
)

api_router.include_router(
    chatbot_router,
    prefix="/chatbot",
    tags=["Chatbot"]
)

api_router.include_router(
    summary_router,
    prefix="/summary",
    tags=["Summary"]
)