"""
Routes pour la gestion des profils utilisateur.

Endpoints:
- POST /start: Crée un nouveau profil utilisateur complet
"""

from fastapi import APIRouter, HTTPException
from app.models.profile_model import UserDocument
from app.services.profile_services import save_user_profile

# Router sans préfixe (ajouté dans routes/__init__.py)
router = APIRouter()

@router.post("/start")
async def create_profile(data: UserDocument) -> dict:
    """
    Endpoint: /profile/start
    Reçoit un profil utilisateur complet (validé par Pydantic),
    l’enregistre dans MongoDB, et renvoie l’ID du document créé.

    """
    try:
        inserted_id = await save_user_profile(data)
        return {
            "message": "Profil enregistré avec succès",
            "id": inserted_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
