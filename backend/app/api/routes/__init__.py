"""
Initialisation des routes de l'API.
"""

from fastapi import APIRouter
from .analyze import router as analyze_router

# Router principal
api_router = APIRouter()

# Inclusion des sous-routes
api_router.include_router(
    analyze_router,
    prefix="/analyze",
    tags=["Analyse"]
)