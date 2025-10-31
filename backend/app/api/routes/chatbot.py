from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models import ChatRequest, ChatResponse
from app.services.cache_service import build_context_for_gemini, add_to_cache, get_user_history, set_user_summary_in_cache
from app.services.stt_service import speech_to_text_service
from app.chatbot.chatbot_agent import call_gemini
from app.chatbot.summary_agent import generate_user_summary
from app.core import logger

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat qui reçoit un message, appelle Gemini avec contexte et sauvegarde"""
    try:
        logger.info(f"💬 Nouveau message de {request.user_id}: {request.message[:50]}...")
        
        # Validation des données
        if not request.message.strip():
            logger.warning("⚠️ Message vide reçu")
            raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")
        
        # Construire le contexte avec l'historique
        message_with_context = build_context_for_gemini(request.user_id, request.message)
        
        # Appeler Gemini avec le contexte
        logger.info("🤖 Appel à Gemini avec contexte en cours...")
        bot_response = await call_gemini(message_with_context)
        
        if "Erreur" in bot_response:
            logger.error(f"❌ Erreur Gemini: {bot_response}")
            return ChatResponse(response=bot_response)
        
        # Ajouter l'échange au cache et vérifier si un résumé doit être généré
        should_generate_summary = add_to_cache(request.user_id, request.message, bot_response)
        
        logger.info("✅ Conversation traitée avec succès")
        
        # Générer le résumé en arrière-plan APRÈS avoir envoyé la réponse (non-bloquant)
        if should_generate_summary:
            # Utiliser asyncio.create_task pour exécution en arrière-plan
            import asyncio
            async def update_summary_background():
                try:
                    logger.info("📊 Génération résumé en arrière-plan (non-bloquant)...")
                    summary_data = await generate_user_summary(request.user_id)
                    if summary_data:
                        set_user_summary_in_cache(request.user_id, summary_data)
                        logger.info("✅ Résumé mis à jour en cache (arrière-plan)")
                except Exception as e:
                    logger.error(f"❌ Erreur résumé arrière-plan: {e}")
            
            # Lancer la tâche en arrière-plan sans attendre
            asyncio.create_task(update_summary_background())
        
        return ChatResponse(response=bot_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur endpoint chat: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du traitement de votre message: {str(e)}"
        )

@router.get("/history/{user_id}")
async def get_conversation_history(user_id: str):
    """Récupère l'historique des conversations d'un utilisateur depuis le cache"""
    try:
        history = get_user_history(user_id)
        return {
            "user_id": user_id,
            "message_count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"❌ Erreur récupération historique: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'historique: {str(e)}")

@router.post("/stt")
async def speech_to_text_endpoint(audio: UploadFile = File(...)):
    """Convertit un fichier audio en texte via Speech-to-Text simplifié"""
    return await speech_to_text_service(audio)