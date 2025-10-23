"""
Routes pour les suggestions holistiques (nutrition + fitness + médical).

Endpoint principal:
- POST /unified: Génère une suggestion unifiée combinant nutrition, fitness et contexte médical
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging
from datetime import datetime

from app.ai.agents.agent_initializer import (
    get_meal_suggestion_agent,
    get_coach_agent,
    get_medical_agent,
    get_orchestrator_agent
)
from app.db.user_store import get_user_document, update_user_document
from app.db.mongo_client import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


async def generate_and_store_suggestions(user_id: str, history_days: int = 7):
    """
    Génère les suggestions et les stocke dans le document utilisateur.
    Fonction appelée en arrière-plan après le scan d'un repas.
    """
    try:
        logger.info(f"🔄 Background task: Generating suggestions for user_id: {user_id}")
        
        # Récupérer les agents
        meal_agent = get_meal_suggestion_agent()
        coach_agent = get_coach_agent()
        medical_agent = get_medical_agent()
        orchestrator = get_orchestrator_agent()
        
        # Générer les suggestions
        meal_result = await meal_agent.generate_suggestions(user_id=user_id, days=history_days)
        workout_result = await coach_agent.generate_suggestions(user_id=user_id, days=history_days)
        
        medical_result = None
        try:
            medical_result = await medical_agent.analyze_medical_context(user_id=user_id)
            if not medical_result.get("success", False):
                medical_result = None
        except Exception:
            medical_result = None
        
        # Orchestrer
        unified_result = orchestrator.orchestrate(
            meal_suggestion=meal_result,
            workout_suggestion=workout_result,
            medical_context=medical_result
        )
        
        if unified_result.get("success", False):
            # Stocker dans le document utilisateur
            last_suggestion = {
                "motivation_message": unified_result.get("motivation_message"),
                "meal_suggestions": unified_result.get("meal_suggestions"),
                "individual_suggestions": unified_result.get("individual_suggestions"),
                "generated_at": unified_result.get("generated_at"),
                "status": "completed"
            }
            
            await update_user_document(user_id, {"last_suggestion": last_suggestion})
            logger.info(f"✅ Suggestions stored for user {user_id}")
        else:
            # Stocker l'erreur
            await update_user_document(user_id, {
                "last_suggestion": {
                    "status": "failed",
                    "error": unified_result.get("error"),
                    "generated_at": datetime.now().isoformat()
                }
            })
            logger.error(f"❌ Failed to generate suggestions for user {user_id}: {unified_result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in background suggestion generation: {e}", exc_info=True)
        try:
            await update_user_document(user_id, {
                "last_suggestion": {
                    "status": "failed",
                    "error": str(e),
                    "generated_at": datetime.now().isoformat()
                }
            })
        except:
            pass


class UnifiedSuggestionRequest(BaseModel):
    """Requête pour générer une suggestion unifiée."""
    user_id: str = Field(..., description="ID de l'utilisateur")
    history_days: int = Field(7, ge=1, le=30, description="Nombre de jours d'historique à analyser")


class UnifiedSuggestionResponse(BaseModel):
    """Réponse contenant la suggestion unifiée."""
    success: bool
    motivation_message: Optional[str] = None
    meal_suggestions: Optional[list] = None
    individual_suggestions: Optional[dict] = None
    user_id: str
    generated_at: str
    error: Optional[str] = None


@router.post("/unified", response_model=UnifiedSuggestionResponse)
async def generate_unified_suggestion(request: UnifiedSuggestionRequest):
    """
    Génère une suggestion holistique unifiée combinant nutrition, fitness et contexte médical.
    
    Processus:
    1. Récupère l'utilisateur par user_id
    2. MealSuggestionAgent génère une suggestion de repas
    3. CoachAgent génère une suggestion d'entraînement
    4. MedicalAgent analyse le contexte médical (optionnel)
    5. OrchestratorAgent combine les trois en une recommandation cohérente
    
    Retourne une suggestion intégrée qui aligne nutrition, fitness et santé.
    """
    try:
        logger.info(f"Generating unified suggestion for user_id: {request.user_id}")
        
        # Étape 0: Vérifier que l'utilisateur existe
        user = await get_user_document(request.user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun utilisateur trouvé avec l'ID: {request.user_id}"
            )
        
        user_id = request.user_id
        
        logger.info(f"User found with user_id: {user_id}")
        
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
            motivation_message=unified_result.get("motivation_message"),
            meal_suggestions=unified_result.get("meal_suggestions"),
            individual_suggestions=unified_result.get("individual_suggestions"),
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


@router.get("/unified/{user_id}")
async def generate_unified_suggestion_by_path(
    user_id: str,
    history_days: int = 7
):
    """
    Alternative avec user_id dans le path.
    
    Exemple: GET /api/suggestions/unified/673c1234567890abcdef1234?history_days=7
    """
    request = UnifiedSuggestionRequest(user_id=user_id, history_days=history_days)
    return await generate_unified_suggestion(request)


@router.get("/motivation/{user_id}")
async def get_motivation_message(user_id: str):
    """
    Retourne uniquement la phrase motivationnelle depuis la dernière suggestion stockée.
    Si aucune suggestion n'existe, retourne un message par défaut.
    """
    try:
        user = await get_user_document(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        last_suggestion = user.get("last_suggestion")
        
        if not last_suggestion:
            return {
                "motivation_message": "Keep scanning your meals! We'll provide personalized suggestions soon.",
                "status": "no_suggestion_yet",
                "generated_at": None
            }
        
        if last_suggestion.get("status") == "failed":
            return {
                "motivation_message": "We're working on your suggestions. Please try again later.",
                "status": "failed",
                "generated_at": last_suggestion.get("generated_at")
            }
        
        return {
            "motivation_message": last_suggestion.get("motivation_message", "Keep up the great work!"),
            "status": "completed",
            "generated_at": last_suggestion.get("generated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching motivation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meals/{user_id}")
async def get_meal_suggestions(user_id: str):
    """
    Retourne uniquement les 5 suggestions de repas depuis la dernière suggestion stockée.
    Si aucune suggestion n'existe, retourne une liste vide.
    """
    try:
        user = await get_user_document(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        last_suggestion = user.get("last_suggestion")
        
        if not last_suggestion:
            return {
                "meal_suggestions": [],
                "status": "no_suggestion_yet",
                "generated_at": None
            }
        
        if last_suggestion.get("status") == "failed":
            return {
                "meal_suggestions": [],
                "status": "failed",
                "error": last_suggestion.get("error"),
                "generated_at": last_suggestion.get("generated_at")
            }
        
        return {
            "meal_suggestions": last_suggestion.get("meal_suggestions", []),
            "status": "completed",
            "generated_at": last_suggestion.get("generated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching meal suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/{user_id}")
async def trigger_suggestion_generation(user_id: str, background_tasks: BackgroundTasks, history_days: int = 7):
    """
    Déclenche la génération de suggestions en arrière-plan.
    Utilisé après le scan d'un repas.
    """
    try:
        user = await get_user_document(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Marquer comme "en cours"
        await update_user_document(user_id, {
            "last_suggestion": {
                "status": "generating",
                "generated_at": datetime.now().isoformat()
            }
        })
        
        # Lancer la tâche en arrière-plan
        background_tasks.add_task(generate_and_store_suggestions, user_id, history_days)
        
        return {
            "success": True,
            "message": "Suggestion generation started in background",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering suggestion generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
