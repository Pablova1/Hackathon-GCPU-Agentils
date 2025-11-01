"""
Routes pour les suggestions de repas personnalisées.


Endpoints:
- POST /generate: Génère une suggestion de repas unique et concise
- GET /health: Vérifie l'état du service
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
import logging

# Import meal agent wrapper from orchestrator
from app.adk.orchestrators.adk_orchestrator import generate_meal_suggestion
from app.adk.config import get_config
from app.db.mongo_client import get_database

logger = logging.getLogger(__name__)

# Router sans préfixe (ajouté dans routes/__init__.py)
router = APIRouter()


class MealSuggestionRequest(BaseModel):
    """Requête pour générer une suggestion de repas."""
    user_id: str = Field(..., description="ID MongoDB de l'utilisateur")
    history_days: int = Field(7, ge=1, le=30, description="Nombre de jours d'historique à analyser")


class MealSuggestionResponse(BaseModel):
    """Réponse contenant la suggestion de repas."""
    success: bool
    suggestion: Optional[str] = None
    user_id: str
    generated_at: str
    error: Optional[str] = None


@router.post("/generate", response_model=MealSuggestionResponse)
async def generate_meal_suggestion(request: MealSuggestionRequest):
    """
    Génère UNE suggestion de repas concise et personnalisée en anglais.
        
    La suggestion est basée sur:
    - Le profil utilisateur (âge, sexe, poids, taille, niveau d'activité)
    - Les objectifs de santé (perte de poids, prise de muscle, etc.)
    - L'historique alimentaire récent (7 derniers jours par défaut)
    - Les allergies et restrictions alimentaires
    
    Retourne une seule ligne en anglais, format:
    "Meal Name: Brief description — ~XXX kcal, macros"
    """
    try:
        # Use meal agent from orchestrator
        result = await generate_meal_suggestion(
            user_id=request.user_id,
            days=request.history_days
        )
        
        # Vérifier le succès
        if not result.get("success", False):
            raise HTTPException(
                status_code=404 if "non trouvé" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Erreur inconnue")
            )
        
        return MealSuggestionResponse(
            success=True,
            suggestion=result.get("suggestion"),
            user_id=request.user_id,
            generated_at=result.get("generated_at", "")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération de suggestion: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne: {str(e)}"
        )


@router.get("/generate/{user_id}")
async def generate_meal_suggestion_by_path(
    user_id: str,
    history_days: int = Query(7, ge=1, le=30, description="Nombre de jours d'historique")
):
    """
    Alternative avec user_id dans le path.
    
    Exemple: GET /api/meal-suggestions/generate/678a7b9c0123456789abcdef?history_days=7
    """
    request = MealSuggestionRequest(user_id=user_id, history_days=history_days)
    return await generate_meal_suggestion(request)


@router.get("/health")
async def health_check():
    """
    Vérifie que l'agent de suggestions de repas est opérationnel.
        
    Retourne:
    - status: "healthy" ou "unhealthy"
    - agent: informations sur l'agent
    - mongodb_connected: état de la connexion MongoDB
    - gemini_configured: état de la configuration Gemini
    """
    try:
        # Get ADK config
        config = get_config()
        
        # Tester la connexion MongoDB (async)
        try:
            db = await get_database()
            collections = await db.list_collection_names()
            mongodb_connected = True
        except:
            mongodb_connected = False
        
        # Vérifier la config Gemini
        gemini_configured = bool(config.client)
        
        status = "healthy" if (mongodb_connected and gemini_configured) else "unhealthy"
        
        return {
            "status": status,
            "agent": {
                "name": "MealSuggestionAgent",
                "model": config.meal_agent_config["model"],
                "type": "pure_adk",
                "ready": True
            },
            "mongodb_connected": mongodb_connected,
            "gemini_configured": gemini_configured
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service indisponible: {str(e)}"
        )
