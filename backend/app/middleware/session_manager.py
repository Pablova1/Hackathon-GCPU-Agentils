"""
Middleware de gestion des sessions utilisateur.
Sessions stockées directement dans la collection 'user' (simplifié pour Hackathon).
"""

from fastapi import Request, HTTPException, Depends, Header
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta
import logging

from app.db.mongo_client import get_database

logger = logging.getLogger(__name__)

# Durée de validité d'une session : 24 heures
SESSION_DURATION = timedelta(hours=24)


class SessionManager:
    """Gestionnaire de sessions utilisateur (stockées dans collection 'user')."""
    
    @staticmethod
    async def create_user_session(user_id: str) -> dict:
        """
        Crée ou renouvelle une session pour un utilisateur.
        Met à jour directement le document user avec le nouveau token.
        
        Args:
            user_id: ID utilisateur (obligatoire)
            
        Returns:
            dict: Session créée avec session_token, user_id, etc.
        """
        db = await get_database()
        users = db["user"]
        
        session_token = str(uuid4())
        now = datetime.now()
        expires_at = now + SESSION_DURATION
        
        # Mise à jour du document user avec le nouveau token
        result = await users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "session_token": session_token,
                    "session_created_at": now,
                    "session_expires_at": expires_at,
                    "last_activity": now,
                    "last_login": now
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Utilisateur {user_id} non trouvé"
            )
        
        session = {
            "session_token": session_token,
            "user_id": user_id,
            "created_at": now,
            "last_activity": now,
            "expires_at": expires_at
        }
        
        logger.info(f"✅ Session créée: {session_token} pour user {user_id}")
        return session
    
    
    @staticmethod
    async def get_session(session_token: str) -> dict:
        """
        Récupère une session et vérifie sa validité.
        
        Args:
            session_token: Token de session
            
        Returns:
            dict: Session avec user_id, created_at, expires_at, last_activity
            
        Raises:
            HTTPException: Si session invalide ou expirée
        """
        db = await get_database()
        users = db["user"]
        
        # Récupérer l'utilisateur par son token de session
        user = await users.find_one({"session_token": session_token})
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Session invalide. Veuillez vous reconnecter."
            )
        
        # Vérification de l'expiration
        session_expires_at = user.get("session_expires_at")
        if not session_expires_at or session_expires_at < datetime.now():
            raise HTTPException(
                status_code=401,
                detail="Session expirée. Veuillez vous reconnecter."
            )
        
        # Mise à jour de la dernière activité
        await users.update_one(
            {"session_token": session_token},
            {"$set": {"last_activity": datetime.now()}}
        )
        
        # Retourner les informations de session
        return {
            "session_token": session_token,
            "user_id": user["user_id"],
            "created_at": user.get("session_created_at"),
            "expires_at": session_expires_at,
            "last_activity": datetime.now()
        }
    
    
    @staticmethod
    async def mark_onboarding_complete(user_id: str):
        """
        Marque l'onboarding comme terminé pour un utilisateur.
        
        Args:
            user_id: ID utilisateur
        """
        db = await get_database()
        users = db["user"]
        
        await users.update_one(
            {"user_id": user_id},
            {"$set": {"profile_completed": True}}
        )
        
        logger.info(f"✅ Onboarding marqué comme complété pour user {user_id}")
    
    
    @staticmethod
    async def get_user_stats(user_id: str) -> dict:
        """
        Récupère les statistiques d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            dict: Statistiques (nombre d'analyses, onboarding, etc.)
        """
        db = await get_database()
        users = db["user"]
        analyses = db["plate_analyses"]
        
        # Récupérer l'utilisateur
        user = await users.find_one({"user_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Compter les analyses
        total_analyses = await analyses.count_documents({"user_id": user_id})
        
        return {
            "user_id": user_id,
            "total_analyses": total_analyses,
            "onboarding_completed": user.get("profile_completed", False),
            "has_active_session": user.get("session_token") is not None
        }
    
    
    @staticmethod
    async def revoke_session(user_id: str):
        """
        Révoque la session d'un utilisateur (déconnexion).
        
        Args:
            user_id: ID utilisateur
        """
        db = await get_database()
        users = db["user"]
        
        await users.update_one(
            {"user_id": user_id},
            {
                "$unset": {
                    "session_token": "",
                    "session_created_at": "",
                    "session_expires_at": ""
                }
            }
        )
        
        logger.info(f"✅ Session révoquée pour user {user_id}")


# Dependency pour extraire la session depuis les headers
async def get_current_session(
    x_session_token: Optional[str] = Header(None)
) -> dict:
    """
    Dependency FastAPI pour récupérer la session courante.
    
    Usage dans une route:
        @router.get("/mon-endpoint")
        async def mon_endpoint(session: dict = Depends(get_current_session)):
            user_id = session["user_id"]
            ...
    
    Args:
        x_session_token: Token de session passé dans les headers
        
    Returns:
        dict: Session courante
        
    Raises:
        HTTPException: Si pas de token ou session invalide
    """
    if not x_session_token:
        raise HTTPException(
            status_code=401,
            detail="Header 'X-Session-Token' manquant. Veuillez créer une session."
        )
    
    return await SessionManager.get_session(x_session_token)


# Dependency optionnelle (ne lève pas d'erreur si pas de session)
async def get_optional_session(
    x_session_token: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Dependency FastAPI pour récupérer la session si elle existe, None sinon.
    Utile pour les endpoints qui peuvent fonctionner avec ou sans session.
    """
    if not x_session_token:
        return None
    
    try:
        return await SessionManager.get_session(x_session_token)
    except HTTPException:
        return None
