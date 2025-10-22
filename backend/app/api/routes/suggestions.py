"""
Routes pour les suggestions holistiques (nutrition + fitness + médical).

Endpoint principal:
- POST /unified: Génère une suggestion unifiée combinant nutrition, fitness et contexte médical
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import logging

from app.ai.agents.agent_initializer import (
    get_meal_suggestion_agent,
    get_coach_agent,
    get_medical_agent,
    get_orchestrator_agent
)
from app.db.user_store import get_user_document_by_email

logger = logging.getLogger(__name__)

router = APIRouter()


class UnifiedSuggestionRequest(BaseModel):
    """Requête pour générer une suggestion unifiée."""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    history_days: int = Field(7, ge=1, le=30, description="Nombre de jours d'historique à analyser")


class UnifiedSuggestionResponse(BaseModel):
    """Réponse contenant la suggestion unifiée."""
    success: bool
    unified_suggestion: Optional[str] = None
    individual_suggestions: Optional[dict] = None
    email: str
    user_id: Optional[str] = None  # Optionnel pour compatibilité
    generated_at: str
    error: Optional[str] = None


@router.post("/unified", response_model=UnifiedSuggestionResponse)
async def generate_unified_suggestion(request: UnifiedSuggestionRequest):
    """
    Génère une suggestion holistique unifiée combinant nutrition, fitness et contexte médical.
    
    Processus:
    1. Récupère l'utilisateur par email
    2. MealSuggestionAgent génère une suggestion de repas
    3. CoachAgent génère une suggestion d'entraînement
    4. MedicalAgent analyse le contexte médical (optionnel)
    5. OrchestratorAgent combine les trois en une recommandation cohérente
    
    Retourne une suggestion intégrée qui aligne nutrition, fitness et santé.
    """
    try:
        logger.info(f"Generating unified suggestion for user email: {request.email}")
        
        # Étape 0: Récupérer l'utilisateur par email
        user = await get_user_document_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun utilisateur trouvé avec l'email: {request.email}"
            )
        
        user_id = user.get("user_id")
        if not user_id:
            # Si user_id n'existe pas, utiliser l'_id MongoDB
            user_id = str(user.get("_id"))
        
        logger.info(f"Found user_id: {user_id} for email: {request.email}")
        
        # Récupérer les 4 agents
        meal_agent = get_meal_suggestion_agent()
        coach_agent = get_coach_agent()
        medical_agent = get_medical_agent()
        orchestrator = get_orchestrator_agent()
        
        # Étape 1: Générer suggestion de repas
        logger.info("Step 1: Generating meal suggestion...")
        meal_result = await meal_agent.generate_suggestions(
            user_id=user_id,
            days=request.history_days
        )
        
        # Étape 2: Générer suggestion d'entraînement
        logger.info("Step 2: Generating workout suggestion...")
        workout_result = await coach_agent.generate_suggestions(
            user_id=user_id,
            days=request.history_days
        )
        
        # Étape 3: Analyser le contexte médical (optionnel - ne pas échouer si erreur)
        logger.info("Step 3: Analyzing medical context...")
        medical_result = None
        try:
            medical_result = await medical_agent.analyze_medical_context(
                user_id=user_id
            )
            if not medical_result.get("success", False):
                logger.warning(f"Medical analysis failed: {medical_result.get('error')}")
                medical_result = None
        except Exception as e:
            logger.warning(f"Medical agent error (continuing without): {e}")
            medical_result = None
        
        # Étape 4: Orchestrer les suggestions
        logger.info("Step 4: Orchestrating suggestions...")
        unified_result = orchestrator.orchestrate(
            meal_suggestion=meal_result,
            workout_suggestion=workout_result,
            medical_context=medical_result
        )
        
        # Vérifier le succès
        if not unified_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=unified_result.get("error", "Erreur lors de l'orchestration")
            )
        
        return UnifiedSuggestionResponse(
            success=True,
            unified_suggestion=unified_result.get("unified_suggestion"),
            individual_suggestions=unified_result.get("individual_suggestions"),
            email=request.email,
            user_id=user_id,
            generated_at=unified_result.get("generated_at")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération unifiée: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating unified suggestion: {str(e)}"
        )


@router.get("/unified/{email}")
async def generate_unified_suggestion_by_path(
    email: str,
    history_days: int = 7
):
    """
    Alternative avec email dans le path.
    
    Exemple: GET /api/suggestions/unified/user@example.com?history_days=7
    """
    request = UnifiedSuggestionRequest(email=email, history_days=history_days)
    return await generate_unified_suggestion(request)


@router.get("/health")
async def health_check():
    """
    Vérifie que tous les agents sont opérationnels.
    """
    try:
        meal_agent = get_meal_suggestion_agent()
        coach_agent = get_coach_agent()
        medical_agent = get_medical_agent()
        orchestrator = get_orchestrator_agent()
        
        # Tester MongoDB
        try:
            await meal_agent.db.list_collection_names()
            mongodb_connected = True
        except:
            mongodb_connected = False
        
        # Vérifier Gemini
        gemini_configured = bool(
            meal_agent.api_key and 
            coach_agent.api_key and 
            medical_agent.api_key and
            orchestrator.api_key
        )
        
        status = "healthy" if (mongodb_connected and gemini_configured) else "unhealthy"
        
        return {
            "status": status,
            "agents": {
                "meal_suggestion": {"ready": True, "model": meal_agent.model_name},
                "coach": {"ready": True, "model": coach_agent.model_name},
                "medical": {"ready": True, "model": medical_agent.model_name},
                "orchestrator": {"ready": True, "model": orchestrator.model_name}
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
