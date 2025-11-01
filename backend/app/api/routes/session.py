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
    Crée une nouvelle session pour un utilisateur existant.
    NOTE: Les sessions sont normalement créées automatiquement lors du login/register.
    Cette route est conservée pour compatibilité mais nécessite un user_id valide.
    
    - **user_id**: (Obligatoire) ID d'un utilisateur existant
    
    Returns:
        SessionResponse avec le token de session et l'user_id
        
    Example:
        ```
        POST /api/session/create
        {
            "user_id": "user_abc123"
        }
        
        Response:
        {
            "session_token": "abc-def-123-456",
            "user_id": "user_abc123",
            "message": "Session créée avec succès"
        }
        ```
    """
    if not request.user_id:
        raise HTTPException(
            status_code=400,
            detail="user_id est obligatoire. Utilisez /api/auth/register pour créer un nouvel utilisateur."
        )
    
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
        "created_at": session.get("created_at"),
        "expires_at": session.get("expires_at"),
        "last_activity": session.get("last_activity")
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
