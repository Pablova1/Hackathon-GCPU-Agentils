"""
Routes pour la gestion des profils utilisateur.

Endpoints:
- GET /check: Vérifie si l'utilisateur a complété son profil
- POST /start: Crée un nouveau profil utilisateur complet
- DELETE /delete: Supprime l'utilisateur et toutes ses données
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.profile_model import UserDocument
from app.services.profile_services import save_user_profile
from app.middleware.session_manager import get_current_session

# Router sans préfixe (ajouté dans routes/__init__.py)
router = APIRouter()

@router.get("/check")
async def check_profile_status(user_id: str = Query(..., description="ID de l'utilisateur")):
    """
    Endpoint: /profile/check
    Vérifie si l'utilisateur a complété son profil d'onboarding.
    
    Retourne:
    {
        "profile_completed": bool,
        "user_exists": bool,
        "profile": {...},  # Données du profil utilisateur
        "onboarding_responses": {...}  # Réponses d'onboarding pour permettre la modification
    }
    """
    try:
        from app.db.mongo_client import get_database
        
        db = await get_database()
        users_collection = db["user"]
        
        user = await users_collection.find_one({"user_id": user_id})
        
        if not user:
            return {
                "profile_completed": False,
                "user_exists": False,
                "profile": None,
                "onboarding_responses": None
            }
        
        # Récupérer le profil utilisateur
        profile = user.get("profile", user.get("profil", {}))
        
        # Récupérer les réponses d'onboarding
        onboarding_responses = user.get("onboarding_responses", {})
        
        # Si les réponses n'existent pas, les reconstruire depuis le profil existant
        if not onboarding_responses and user.get("profile_completed", False):
            onboarding_responses = reconstruct_onboarding_responses(user)
            
            # Sauvegarder les réponses reconstruites pour les futures requêtes
            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"onboarding_responses": onboarding_responses}}
            )
        
        return {
            "profile_completed": user.get("profile_completed", False),
            "user_exists": True,
            "profile": profile,
            "onboarding_responses": onboarding_responses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

@router.post("/start")
async def create_profile(data: UserDocument) -> dict:
    """
    Endpoint: /profile/start
    Reçoit un profil utilisateur complet (validé par Pydantic),
    l'enregistre dans MongoDB, et renvoie l'ID du document créé.

    """
    try:
        inserted_id = await save_user_profile(data)
        return {
            "message": "Profil enregistré avec succès",
            "id": inserted_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


@router.delete("/delete")
async def delete_user_profile(session: dict = Depends(get_current_session)):
    """
    Endpoint: /profile/delete
    Supprime l'utilisateur et toutes ses données (repas, analyses, etc.).
    
    Requiert une session valide via le header X-Session-Token.
    """
    try:
        from app.db.mongo_client import get_database
        from app.db.meal_store import delete_user_meals
        
        user_id = session["user_id"]
        
        db = await get_database()
        
        # 1. Supprimer tous les repas de l'utilisateur
        meals_deleted = await delete_user_meals(user_id)
        
        # 2. Supprimer l'utilisateur
        users_collection = db["user"]
        result = await users_collection.delete_one({"user_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return {
            "message": "Utilisateur et toutes ses données supprimés avec succès",
            "user_id": user_id,
            "meals_deleted": meals_deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


def reconstruct_onboarding_responses(user: dict) -> dict:
    """
    Reconstruit les réponses d'onboarding à partir des données du profil MongoDB.
    Utilisé pour les utilisateurs qui ont complété leur profil avant l'ajout du champ onboarding_responses.
    """
    responses = {}
    
    profile = user.get("profile", {})
    medical = user.get("medical", {})
    nutrition = user.get("nutrition", {})
    goals = user.get("goals", {})
    misc = user.get("misc", {})
    religious = user.get("religiousRestrictions", {})
    
    # Informations de base
    if profile.get("age"):
        # Calculer birthDate approximative depuis age
        from datetime import datetime
        current_year = datetime.now().year
        birth_year = current_year - int(profile["age"])
        responses["birthDate"] = f"{birth_year}-01-01"
    
    if profile.get("gender"):
        responses["gender"] = profile["gender"]
    
    if profile.get("height"):
        responses["heightCm"] = str(profile["height"])
    
    if profile.get("weight"):
        responses["weightKg"] = str(profile["weight"])
    
    if profile.get("bodyType"):
        responses["bodyType"] = profile["bodyType"]
    
    # Nutrition
    if nutrition.get("diet"):
        responses["dietType"] = nutrition["diet"]
    
    if medical.get("allergies"):
        responses["allergies"] = medical["allergies"]
    
    if nutrition.get("intolerances"):
        responses["intolerances"] = nutrition["intolerances"]
    
    preferences = nutrition.get("preferences", {})
    if preferences.get("liked"):
        responses["foodLikes"] = preferences["liked"]
    
    if preferences.get("disliked"):
        responses["foodDislikes"] = preferences["disliked"]
    
    if preferences.get("general"):
        responses["foodPreferences"] = preferences["general"]
    
    # Santé
    if medical.get("treatments"):
        responses["treatments"] = medical["treatments"]
    
    medical_history = medical.get("medicalHistory", {})
    if medical_history.get("personal"):
        responses["medicalHistoryPersonal"] = medical_history["personal"]
    
    if medical_history.get("family"):
        responses["medicalHistoryFamily"] = medical_history["family"]
    
    birth_control = medical.get("birthControl")
    if birth_control:
        responses["birthControl"] = "Oui" if birth_control.get("uses") else "Non"
        if birth_control.get("name"):
            responses["birthControlName"] = birth_control["name"]
    
    # Objectifs
    if goals.get("muscleGain") is not None:
        responses["goalMuscleGain"] = "Oui" if goals["muscleGain"] else "Non"
    
    if goals.get("weightLoss") is not None:
        responses["goalWeightLoss"] = "Oui" if goals["weightLoss"] else "Non"
    
    if goals.get("performance") is not None:
        responses["goalPerformance"] = "Oui" if goals["performance"] else "Non"
    
    if goals.get("maintainShape") is not None:
        responses["goalMaintainShape"] = "Oui" if goals["maintainShape"] else "Non"
    
    if goals.get("goalDetail"):
        responses["goalDetail"] = goals["goalDetail"]
    
    # Restrictions religieuses
    if religious:
        responses["religiousPracticing"] = "Oui" if religious.get("practicing") else "Non"
        if religious.get("type"):
            responses["religiousType"] = religious["type"]
    
    # Activité et mode de vie
    if misc.get("activityLevel"):
        responses["activityLevel"] = misc["activityLevel"]
    
    if misc.get("sports"):
        responses["sports"] = misc["sports"]
    
    if misc.get("occupation"):
        responses["occupation"] = misc["occupation"]
    
    if misc.get("notes"):
        responses["additionalNotes"] = misc["notes"]
    
    return responses
