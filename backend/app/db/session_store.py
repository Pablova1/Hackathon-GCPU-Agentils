from uuid import uuid4
from datetime import datetime

# Stockage en mémoire (MVP)
SESSIONS: dict[str, dict] = {}

def create_session(user_id: str) -> dict:
    if not user_id:
        raise ValueError("user_id manquant")
    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "state": "ASKING_QUESTIONS",
        "slots": {},
        "created_at": datetime.now().isoformat()
    }
    SESSIONS[session_id] = session
    return session

def get_session(session_id: str) -> dict | None:
    return SESSIONS.get(session_id)
