from fastapi import APIRouter, HTTPException
from app.models import SummaryResponse
from app.services.cache_service import get_user_history, get_user_summary_from_cache, set_user_summary_in_cache
from app.chatbot.summary_agent import generate_user_summary
from app.core import logger

router = APIRouter()

@router.get("/summary/{user_id}", response_model=SummaryResponse)
async def get_user_summary(user_id: str):
    """
    Récupère le résumé utilisateur depuis le cache (mis à jour après chaque message)
    """
    try:
        logger.info(f"📊 Récupération résumé depuis cache pour {user_id}")
        
        # Vérifier si un résumé est disponible en cache
        cached_summary = get_user_summary_from_cache(user_id)
        if cached_summary:
            logger.info(f"✅ Résumé trouvé en cache pour {user_id}")
            return SummaryResponse(**cached_summary)
        
        # Si pas de cache, générer un nouveau résumé
        logger.info(f"🆕 Aucun cache trouvé, génération du premier résumé pour {user_id}")
        
        # Récupérer l'historique de l'utilisateur
        history = get_user_history(user_id)
        
        if not history:
            return SummaryResponse(
                user_id=user_id,
                summary="Aucun historique de conversation disponible.",
                message_count=0
            )
        
        # Générer le résumé et le mettre en cache
        summary_data = await generate_user_summary(user_id)
        if summary_data:
            set_user_summary_in_cache(user_id, summary_data)
            return SummaryResponse(**summary_data)
        else:
            return SummaryResponse(
                user_id=user_id,
                summary="Erreur lors de la génération du résumé.",
                message_count=len(history)
            )
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération résumé: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du résumé: {str(e)}")