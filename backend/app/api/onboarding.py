from fastapi import APIRouter, HTTPException, Query
from app.db.session_store import create_session
from app.services.onboarding_planner import first_question
from app.ai.onboarding_ai import suggest_followup

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.post("/start")
async def start(user_id: str = Query(..., description="ID de l'utilisateur qui démarre l'onboarding")):
    """
    Crée une session d'onboarding et renvoie la première question.
    Réponse:
    {
      "session_id": "...",
      "question": { "slot": "...", "text": "...", "type": "...", "choices": [...]? }
    }
    """
    try:
        session = create_session(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    question = first_question()
    return {"session_id": session["session_id"], "question": question}


from fastapi import APIRouter, HTTPException, Query
from app.db.session_store import create_session, get_session
from app.services.onboarding_planner import first_question, next_required_slot, question_for_slot

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.get("/next")
async def next_question(session_id: str = Query(..., description="ID de session d'onboarding")):
    """
    Renvoie la prochaine question à poser, ou finished=true si toutes les questions fixes sont remplies.
    Réponse:
    {
      "session_id": "...",
      "finished": false,
      "question": { "slot": "...", "text": "...", "type": "...", "choices": [...]? }
    }
    ou
    {
      "session_id": "...",
      "finished": true,
      "profile_preview": { ...slots... }
    }
    """
    sess = get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session inconnue")

    slots = sess["slots"]
    nxt = next_required_slot(slots)

    if nxt is None:
        # Appel à l’IA avant de terminer
        asked_ai_count = sess.get("asked_ai_count", 0)
        ai_question = suggest_followup(slots, asked_ai_count)

        if ai_question:
            # marquer qu’on a posé une question IA
            sess["asked_ai_count"] = asked_ai_count + 1
            return {
                "session_id": session_id,
                "finished": False,
                "question": ai_question
            }

        # sinon, profil terminé
        return {
            "session_id": session_id,
            "finished": True,
            "profile_preview": slots
        }