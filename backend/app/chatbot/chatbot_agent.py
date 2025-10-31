import requests
import json
import time
from app.core import GOOGLE_API_KEY, logger
from app.chatbot.prompts.chatbot_prompts import CHATBOT_SYSTEM_PROMPT, build_chatbot_prompt

def retry_on_failure(max_retries=2, delay=2):
    """Décorateur simple pour retry automatique"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except requests.exceptions.Timeout:
                    if attempt == max_retries - 1:
                        logger.error("❌ Timeout final - fallback")
                        return "Désolé, je rencontre actuellement des difficultés techniques. Pouvez-vous reformuler votre question ?"
                    logger.warning(f"⏱️ Timeout tentative {attempt + 1}/{max_retries}")
                    if attempt > 0:
                        time.sleep(delay)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"❌ Erreur réseau tentative {attempt + 1}: {e}")
                    if attempt > 0:
                        time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=2, delay=2)
async def call_gemini(message: str) -> str:
    """Appelle Gemini via API REST avec retry automatique"""
    logger.info(f"🤖 Appel Gemini: message_longueur={len(message)}")
    logger.info(f"📝 Message reçu: {message[:100]}...")
    
    try:
        # Validation du message
        if not message or len(message.strip()) == 0:
            logger.warning("⚠️ Message vide pour Gemini")
            return "Erreur: Message vide"
        
        # URL de l'API Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        # Construire le prompt complet
        full_prompt = build_chatbot_prompt(CHATBOT_SYSTEM_PROMPT, message)

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        
        logger.info(" Appel API Gemini...")
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        # Gestion des erreurs HTTP
        if response.status_code == 503:
            logger.warning("🚦 API temporairement surchargée")
            return "L'assistant est temporairement surchargé. Veuillez réessayer dans quelques instants."
        
        logger.info(f"📥 Réponse reçue: status={response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    response_text = candidate["content"]["parts"][0]["text"]
                    logger.info(f"✅ Réponse générée: longueur={len(response_text)}")
                    return response_text
                else:
                    logger.error("❌ Structure de réponse Gemini inattendue")
                    return "Erreur: Réponse Gemini malformée"
            else:
                logger.error("❌ Aucun candidat dans la réponse Gemini")
                return "Erreur: Aucune réponse générée par Gemini"
        else:
            error_detail = response.text
            logger.error(f"❌ Erreur API Gemini: {response.status_code}")
            logger.error(f"📄 Corps de l'erreur: {error_detail}")
            return f"Erreur API Gemini: {response.status_code}"
            
    except Exception as e:
        logger.error(f"❌ Erreur Gemini: {e}")
        return f"Erreur Gemini: {str(e)}"