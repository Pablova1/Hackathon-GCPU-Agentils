"""
Initialisation des routes de l'API.

Ce fichier agrège tous les routers de l'application.
Tous les endpoints sont préfixés par /api dans main.py
"""

from fastapi import APIRouter
from .analyze import router as analyze_router
from .onboarding import router as onboarding_router
from .profile import router as profile_router
from .meal_suggestions import router as meal_suggestions_router

# Router principal qui agrège toutes les routes
api_router = APIRouter()

# Inclusion des sous-routes
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
    meal_suggestions_router,
    prefix="/meal-suggestions",
    tags=["Meal Suggestions"]
)