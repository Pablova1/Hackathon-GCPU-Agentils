from collections import deque
from datetime import datetime
from typing import Dict, List
from app.core.config import MAX_MESSAGES_PER_USER, logger

# Cache mémoire pour l'historique des conversations (20 messages max par utilisateur)
conversation_cache: Dict[str, deque] = {}
# Cache pour les résumés utilisateur (mis à jour après chaque message)
user_summaries_cache: Dict[str, dict] = {}

def get_user_history(user_id: str) -> List[Dict]:
    """Récupère l'historique d'un utilisateur depuis le cache"""
    if user_id not in conversation_cache:
        conversation_cache[user_id] = deque(maxlen=MAX_MESSAGES_PER_USER)
    return list(conversation_cache[user_id])

def add_to_cache(user_id: str, user_message: str, bot_response: str) -> bool:
    """Ajoute un échange à l'historique de l'utilisateur"""
    if user_id not in conversation_cache:
        conversation_cache[user_id] = deque(maxlen=MAX_MESSAGES_PER_USER)
    
    conversation_cache[user_id].append({
        "user": user_message,
        "assistant": bot_response,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    message_count = len(conversation_cache[user_id])
    logger.info(f"📝 Cache mis à jour pour {user_id}: {message_count} messages")
    
    # Maintenant on génère un résumé après CHAQUE message (en arrière-plan)
    return True  # Toujours générer un résumé

def build_context_for_gemini(user_id: str, current_message: str) -> str:
    """Construit le contexte avec l'historique pour Gemini (version simplifiée)"""
    history = get_user_history(user_id)
    
    # Pour la première requête, retourner directement le message
    if not history:
        logger.info("🚀 Première requête - pas de contexte")
        return current_message
    
    # Limiter à 5 échanges récents pour optimiser
    recent_history = history[-5:]
    
    # Construction du contexte avec template simple
    context_parts = [f"Contexte ({len(recent_history)} échanges):"]
    
    for exchange in recent_history:
        context_parts.append(f"U: {exchange['user']}")
        context_parts.append(f"A: {exchange['assistant']}")
    
    context_parts.append(f"\nNouvelle question: {current_message}")
    
    full_context = "\n".join(context_parts)
    logger.info(f"🧠 Contexte: {len(recent_history)} échanges, {len(full_context)} chars")
    return full_context

def get_user_summary_from_cache(user_id: str) -> dict:
    """Récupère le résumé utilisateur depuis le cache"""
    return user_summaries_cache.get(user_id)

def set_user_summary_in_cache(user_id: str, summary_data: dict):
    """Stocke le résumé utilisateur dans le cache"""
    user_summaries_cache[user_id] = summary_data