"""
Routes pour la gestion des sessions utilisateur.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.middleware.session_manager import SessionManager, get_current_session

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Requête pour créer une session."""
    user_id: Optional[str] = None  # Optionnel : si non fourni, généré automatiquement


class SessionResponse(BaseModel):
    """Réponse avec les informations de session."""
    session_token: str
    user_id: str
    message: str


@router.post("/create", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Crée une nouvelle session utilisateur.
    
    - **user_id**: (Optionnel) ID utilisateur. Si non fourni, un ID sera généré automatiquement.
    
    Returns:
        SessionResponse avec le token de session et l'user_id
        
    Example:
        ```
        POST /api/session/create
        {
            "user_id": "mon_utilisateur_123"  // optionnel
        }
        
        Response:
        {
            "session_token": "abc-def-123-456",
            "user_id": "mon_utilisateur_123",
            "message": "Session créée avec succès"
        }
        ```
    """
    session = await SessionManager.create_user_session(request.user_id)
    
    return SessionResponse(
        session_token=session["session_token"],
        user_id=session["user_id"],
        message="Session créée avec succès. Utilisez 'X-Session-Token' dans les headers."
    )


@router.get("/info")
async def get_session_info(session: dict = Depends(get_current_session)):
    """
    Récupère les informations de la session courante.
    
    Headers requis:
        - X-Session-Token: Token de session
        
    Returns:
        Informations détaillées sur la session
        
    Example:
        ```
        GET /api/session/info
        Headers: X-Session-Token: abc-def-123-456
        
        Response:
        {
            "session_token": "abc-def-123-456",
            "user_id": "mon_utilisateur_123",
            "created_at": "2025-10-20T10:30:00",
            "last_activity": "2025-10-20T15:45:00",
            "metadata": {
                "onboarding_completed": true,
                "total_analyses": 5
            }
        }
        ```
    """
    return {
        "session_token": session["session_token"],
        "user_id": session["user_id"],
        "created_at": session["created_at"],
        "last_activity": session["last_activity"],
        "metadata": session.get("metadata", {})
    }


@router.get("/stats/{user_id}")
async def get_user_statistics(user_id: str):
    """
    Récupère les statistiques d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    
    Returns:
        Statistiques globales de l'utilisateur
        
    Example:
        ```
        GET /api/session/stats/mon_utilisateur_123
        
        Response:
        {
            "user_id": "mon_utilisateur_123",
            "total_sessions": 3,
            "total_analyses": 15,
            "onboarding_completed": true
        }
        ```
    """
    stats = await SessionManager.get_user_stats(user_id)
    return stats


@router.post("/validate")
async def validate_session(session: dict = Depends(get_current_session)):
    """
    Valide que la session est encore active.
    
    Headers requis:
        - X-Session-Token: Token de session
        
    Returns:
        Confirmation de validité
    """
    return {
        "valid": True,
        "user_id": session["user_id"],
        "message": "Session valide"
    }
