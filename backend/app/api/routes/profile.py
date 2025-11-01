"""
Routes pour la gestion des profils utilisateur.

Endpoints:
- POST /start: Crée un nouveau profil utilisateur complet
- GET /check: Vérifie si le profil est complété et retourne les réponses d'onboarding
- DELETE /delete: Supprime l'utilisateur et toutes ses données
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.profile_model import UserDocument
from app.services.profile_services import save_user_profile
from app.middleware.session_manager import get_current_session

# Router sans préfixe (ajouté dans routes/__init__.py)
router = APIRouter()


@router.get("/check")
async def check_profile(user_id: str = Query(..., description="ID de l'utilisateur")):
    """
    Vérifie si le profil utilisateur est complété et retourne les réponses d'onboarding.
    Utilisé par le frontend pour charger les réponses existantes en mode édition.
    """
    from app.db.mongo_client import get_database
    
    db = await get_database()
    users = db["user"]
    
    # Chercher l'utilisateur
    user = await users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    profile_completed = user.get("profile_completed", False)
    onboarding_responses = user.get("onboarding_responses", {})
    
    return {
        "user_id": user_id,
        "profile_completed": profile_completed,
        "onboarding_responses": onboarding_responses
    }


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
        
        # 2. Supprimer les analyses d'assiettes
        plate_analyses = db["plate_analyses"]
        await plate_analyses.delete_many({"user_id": user_id})
        
        # 3. Supprimer les analyses nutritionnelles
        nutrient_analyses = db["nutrient_analyses"]
        await nutrient_analyses.delete_many({"user_id": user_id})
        
        # 4. Supprimer l'utilisateur
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
