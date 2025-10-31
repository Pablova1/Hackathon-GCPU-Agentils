from datetime import datetime
from app.core import logger
from app.services import get_user_history
from app.chatbot.chatbot_agent import call_gemini
from app.chatbot.prompts.summary_prompts import build_summary_prompt

async def generate_user_summary(user_id: str) -> dict:
    """
    Génère automatiquement un résumé concis des besoins de l'utilisateur
    basé sur l'historique complet (analyse après chaque message)
    """
    try:
        logger.info(f"📊 Génération résumé en arrière-plan pour {user_id}")
        
        # Récupérer l'historique de l'utilisateur
        history = get_user_history(user_id)
        
        if not history:
            return None
        
        # Analyser TOUT l'historique (pas seulement les 10 derniers)
        conversation_text = []
        for exchange in history:
            conversation_text.append(f"Utilisateur: {exchange['user']}")
            conversation_text.append(f"Assistant: {exchange['assistant']}")
        
        # Construire le prompt d'analyse
        analysis_prompt = build_summary_prompt("\n".join(conversation_text))
        
        # Appeler Gemini pour l'analyse
        logger.info("🧠 Analyse automatique (arrière-plan) des besoins utilisateur...")
        summary = await call_gemini(analysis_prompt)
        
        logger.info(f"✅ Résumé en arrière-plan généré pour {user_id}")
        return {
            "user_id": user_id,
            "summary": summary,
            "message_count": len(history),
            "total_conversations": len(history),
            "generated_at": datetime.utcnow().isoformat(),
            "auto_generated": True
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur génération automatique du résumé: {e}")
        return None