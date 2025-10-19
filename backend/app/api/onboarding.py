from fastapi import APIRouter, HTTPException, Query, Body
from app.db.session_store import create_session, get_session, update_session
from app.db.user_store import create_user_document
from app.services.onboarding_planner import QUESTION_BANK, first_question, next_required_slot, question_for_slot
from app.ai.agents.agent_onboarding.agent import suggest_followup
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class AnswerRequest(BaseModel):
    session_id: str
    slot: str
    value: str | int | float


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
        session = await create_session(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    question = first_question()
    return {"session_id": session["session_id"], "question": question}


@router.post("/answer")
async def answer_question(request: AnswerRequest):
    """Enregistre une réponse et retourne la prochaine question."""
    sess = await get_session(request.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session inconnue")
    
    # Valider le type de réponse selon la question
    if not validate_answer(request.slot, request.value):
        raise HTTPException(status_code=400, detail=f"Réponse invalide pour {request.slot}")
    
    # Enregistrer la réponse
    slots = sess.get("slots", {})
    slots[request.slot] = request.value
    
    # Si c'est une question IA, stocker aussi le texte de la question
    if request.slot.startswith("ai_followup_"):
        last_ai_questions = sess.get("last_ai_questions", {})
        if request.slot in last_ai_questions:
            slots[f"{request.slot}_question"] = last_ai_questions[request.slot]
    
    await update_session(request.session_id, {"slots": slots})
    
    # Déterminer la prochaine question
    nxt = next_required_slot(slots)
    
    if nxt is not None:
        return {
            "session_id": request.session_id,
            "accepted": True,
            "finished": False,
            "next_question": question_for_slot(nxt)
        }
    
    # Toutes les questions requises sont répondues → créer l'utilisateur IMMÉDIATEMENT
    user_id = sess.get("user_id")
    mapped = map_minimal_slots_to_full_profile(slots)
    
    # Créer l'utilisateur seulement s'il n'existe pas déjà
    user_doc_id = sess.get("user_document_id")
    if not user_doc_id:
        try:
            logger.info(f"Création de l'utilisateur {user_id}")
            user_doc = await create_user_document(user_id, mapped)
            user_doc_id = user_doc.get("_id")
            logger.info(f"Utilisateur créé avec l'ID: {user_doc_id}")
            await update_session(request.session_id, {"user_document_id": user_doc_id})
        except Exception as e:
            logger.error(f"ERREUR lors de la création de l'utilisateur: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erreur création profil: {str(e)}")
    else:
        # L'utilisateur existe déjà, mettre à jour avec les nouvelles réponses IA
        logger.info(f"Utilisateur déjà créé avec l'ID: {user_doc_id}, mise à jour avec réponses IA")
        try:
            # Mettre à jour seulement le champ notes avec les réponses IA
            if mapped.get("notes"):
                from app.db.user_store import update_user_document
                await update_user_document(user_id, {"misc.notes": mapped["notes"]})
                logger.info(f"Notes IA mises à jour pour l'utilisateur {user_id}")
        except Exception as e:
            logger.error(f"ERREUR lors de la mise à jour des notes IA: {str(e)}", exc_info=True)
    
    # Ensuite, proposer des questions IA supplémentaires (optionnelles)
    asked_ai_count = sess.get("asked_ai_count", 0)
    ai_question = suggest_followup(slots, asked_ai_count)
    
    if ai_question:
        new_count = asked_ai_count + 1
        # Stocker le texte de la question IA pour pouvoir le récupérer plus tard
        last_ai_questions = sess.get("last_ai_questions", {})
        last_ai_questions[ai_question["slot"]] = ai_question["text"]
        await update_session(request.session_id, {
            "asked_ai_count": new_count,
            "last_ai_questions": last_ai_questions
        })
        return {
            "session_id": request.session_id,
            "accepted": True,
            "finished": False,
            "next_question": ai_question,
            "user_created": True,
            "user_document_id": user_doc_id,
            "message": "Profil créé, questions supplémentaires disponibles"
        }
    
    # Toutes les questions (obligatoires + IA) sont terminées
    await update_session(request.session_id, {"state": "COMPLETED"})
    return {
        "session_id": request.session_id,
        "accepted": True,
        "finished": True,
        "next_question": None,
        "profile_preview": slots,
        "user_created": True,
        "user_document_id": user_doc_id,
        "message": "Profil créé avec succès"
    }


def validate_answer(slot: str, value) -> bool:
    """Valide le type de réponse."""
    q = QUESTION_BANK.get(slot)
    if not q:
        return True  # Questions IA : pas de validation stricte
    
    qtype = q.get("type")
    if qtype == "number":
        try:
            float(value)
            return True
        except:
            return False
    elif qtype == "single_choice":
        return value in q.get("choices", [])
    
    return True  # text : tout est accepté

@router.get("/next")
async def next_question(session_id: str = Query(...)):
    """Retourne la prochaine question."""
    sess = await get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session inconnue")
    
    slots = sess.get("slots", {})
    nxt = next_required_slot(slots)
    
    if nxt is not None:
        return {
            "session_id": session_id,
            "finished": False,
            "question": question_for_slot(nxt)
        }
    
    # Questions requises terminées → appeler l'IA
    asked_ai_count = sess.get("asked_ai_count", 0)
    ai_question = suggest_followup(slots, asked_ai_count)
    
    if ai_question:
        # IMPORTANT : Persister le compteur et stocker le texte de la question
        new_count = asked_ai_count + 1
        last_ai_questions = sess.get("last_ai_questions", {})
        last_ai_questions[ai_question["slot"]] = ai_question["text"]
        await update_session(session_id, {
            "asked_ai_count": new_count,
            "last_ai_questions": last_ai_questions
        })
        
        return {
            "session_id": session_id,
            "finished": False,
            "question": ai_question
        }
    
    # Tout est terminé
    return {
        "session_id": session_id,
        "finished": True,
        "profile_preview": slots
    }
@router.post("/end")
async def end_onboarding(session_id: str = Query(..., description="ID de la session d'onboarding")):
    """
    Termine l'onboarding : marque la session comme complète, crée le document utilisateur
    dans la collection 'users' avec le bon modèle ProfileCore, et renvoie le profil final.
    """
    sess = await get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session inconnue")

    user_id = sess.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id manquant dans la session")

    slots = sess.get("slots", {})

    # Calcul IMC (optionnel)
    if "height_cm" in slots and "weight_kg" in slots:
        try:
            h = float(slots["height_cm"])
            w = float(slots["weight_kg"])
            bmi = round(w / ((h / 100) ** 2), 1)
            slots["bmi"] = bmi
        except Exception:
            pass

    # Mapper les slots minimalistes vers le modèle UserDocument complet
    mapped_slots = map_minimal_slots_to_full_profile(slots)
    
    # Créer le document utilisateur dans la collection 'users'
    try:
        user_doc = await create_user_document(user_id, mapped_slots)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du profil utilisateur: {str(e)}")
    
    # Mettre à jour la session comme complétée
    await update_session(session_id, {"state": "COMPLETED"})

    return {
        "status": "completed",
        "session_id": session_id,
        "user_id": user_id,
        "profile": slots,
        "user_document_id": user_doc.get("_id"),
        "message": "Profil utilisateur créé avec succès dans la collection 'users'"
    }


def map_minimal_slots_to_full_profile(slots: dict) -> dict:
    """Mappe les slots de l'onboarding vers le modèle UserDocument complet."""
    
    # Calculer l'âge depuis la date de naissance
    age = 0
    if "birthDate" in slots:
        try:
            birth_date = datetime.strptime(slots["birthDate"], "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except:
            age = 0
    
    # Extraire les réponses IA (slots qui commencent par "ai_followup_")
    # et stocker aussi les questions IA associées
    ai_entries = []
    regular_slots = {}
    
    for key, value in slots.items():
        if key.startswith("ai_followup_"):
            # Récupérer la question associée depuis la session si disponible
            question_text = slots.get(f"{key}_question", "Question IA")
            ai_entries.append(f"Q: {question_text} | R: {value}")
        elif not key.endswith("_question"):  # Ignorer les clés de questions stockées
            regular_slots[key] = value
    
    # Créer une note avec les questions et réponses IA
    notes = None
    if ai_entries:
        notes = "Informations supplémentaires - " + " || ".join(ai_entries)
    
    return {
        # ProfileCore
        "firstName": regular_slots.get("firstName", ""),
        "lastName": regular_slots.get("lastName", ""),
        "age": age,
        "gender": regular_slots.get("gender", "Other"),
        "weight_kg": float(regular_slots.get("weightKg", 0)) if regular_slots.get("weightKg") else 0.0,
        "height_cm": float(regular_slots.get("heightCm", 0)) if regular_slots.get("heightCm") else 0.0,
        "bodyType": regular_slots.get("bodyType", "unknown"),
        
        # Medical
        "treatments": [],
        "allergies": [],
        "medicalHistory_personal": [],
        "medicalHistory_family": [],
        "birthControl_uses": False,
        
        # Nutrition
        "diet": regular_slots.get("dietType"),
        "intolerances": [],
        "preferences_liked": [],
        "preferences_disliked": [],
        "preferences_general": [],
        
        # Goals
        "muscleGain": False,
        "weightLoss": False,
        "goalDetail": None,
        "performance": False,
        "maintainShape": False,
        
        # Misc (avec les questions et réponses IA dans notes)
        "activityLevel": regular_slots.get("activityLevel"),
        "sports": [],
        "occupation": None,
        "notes": notes,  # Les questions et réponses IA sont stockées ici
    }