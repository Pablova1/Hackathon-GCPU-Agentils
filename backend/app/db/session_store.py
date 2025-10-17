from uuid import uuid4
from datetime import datetime
from app.db.mongo_client import get_database

async def create_session(user_id: str) -> dict:
    """
    Crée une session d'onboarding et l'enregistre dans MongoDB.
    """
    if not user_id:
        raise ValueError("user_id manquant")
    
    db = await get_database()
    sessions_collection = db["onboarding_sessions"]
    
    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "state": "ASKING_QUESTIONS",
        "slots": {},
        "asked_ai_count": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await sessions_collection.insert_one(session)
    return session


async def get_session(session_id: str) -> dict | None:
    """
    Récupère une session d'onboarding par son ID.
    """
    db = await get_database()
    sessions_collection = db["onboarding_sessions"]
    
    session = await sessions_collection.find_one({"session_id": session_id})
    return session


async def update_session(session_id: str, updates: dict) -> dict | None:
    """
    Met à jour une session.
    """
    db = await get_database()
    sessions_collection = db["onboarding_sessions"]
    
    result = await sessions_collection.find_one_and_update(
        {"session_id": session_id},
        {"$set": updates},
        return_document=True
    )
    return result