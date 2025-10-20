"""
Middleware de gestion des sessions utilisateur.
Permet de tracker les utilisateurs à travers leurs actions (onboarding, analyses, etc.).
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
    """Gestionnaire de sessions utilisateur."""
    
    @staticmethod
    async def create_user_session(user_id: Optional[str] = None) -> dict:
        """
        Crée une nouvelle session utilisateur.
        
        Args:
            user_id: ID utilisateur optionnel (sinon généré automatiquement)
            
        Returns:
            dict: Session créée avec session_token, user_id, etc.
        """
        db = await get_database()
        sessions = db["user_sessions"]
        
        # Génération d'un user_id si non fourni
        if not user_id:
            user_id = f"user_{uuid4().hex[:12]}"
        
        session_token = str(uuid4())
        
        session = {
            "session_token": session_token,
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "expires_at": datetime.now() + SESSION_DURATION,
            "metadata": {
                "onboarding_completed": False,
                "total_analyses": 0
            }
        }
        
        # Insertion dans MongoDB
        await sessions.insert_one(session)
        
        logger.info(f"✅ Session créée: {session_token} pour user {user_id}")
        return session
    
    
    @staticmethod
    async def get_session(session_token: str) -> dict:
        """
        Récupère une session et vérifie sa validité.
        
        Args:
            session_token: Token de session
            
        Returns:
            dict: Session si valide
            
        Raises:
            HTTPException: Si session invalide ou expirée
        """
        db = await get_database()
        sessions = db["user_sessions"]
        
        session = await sessions.find_one({"session_token": session_token})
        
        if not session:
            raise HTTPException(
                status_code=401,
                detail="Session invalide. Veuillez créer une nouvelle session."
            )
        
        # Vérification de l'expiration
        if session["expires_at"] < datetime.now():
            raise HTTPException(
                status_code=401,
                detail="Session expirée. Veuillez vous reconnecter."
            )
        
        # Mise à jour de la dernière activité
        await sessions.update_one(
            {"session_token": session_token},
            {
                "$set": {"last_activity": datetime.now()},
                "$inc": {"metadata.total_requests": 1}
            }
        )
        
        return session
    
    
    @staticmethod
    async def update_session_metadata(session_token: str, updates: dict):
        """
        Met à jour les métadonnées d'une session.
        
        Args:
            session_token: Token de session
            updates: Dictionnaire de mises à jour (ex: {"metadata.total_analyses": 1})
        """
        db = await get_database()
        sessions = db["user_sessions"]
        
        await sessions.update_one(
            {"session_token": session_token},
            {"$inc": updates}
        )
    
    
    @staticmethod
    async def mark_onboarding_complete(session_token: str):
        """Marque l'onboarding comme terminé pour une session."""
        db = await get_database()
        sessions = db["user_sessions"]
        
        await sessions.update_one(
            {"session_token": session_token},
            {"$set": {"metadata.onboarding_completed": True}}
        )
        
        logger.info(f"✅ Onboarding marqué comme complété pour session {session_token}")
    
    
    @staticmethod
    async def get_user_stats(user_id: str) -> dict:
        """
        Récupère les statistiques d'un utilisateur.
        
        Args:
            user_id: ID utilisateur
            
        Returns:
            dict: Statistiques (nombre d'analyses, sessions, etc.)
        """
        db = await get_database()
        sessions = db["user_sessions"]
        analyses = db["plate_analyses"]
        
        # Récupérer toutes les sessions de l'utilisateur
        user_sessions = await sessions.find({"user_id": user_id}).to_list(None)
        
        # Compter les analyses
        total_analyses = await analyses.count_documents({"user_id": user_id})
        
        return {
            "user_id": user_id,
            "total_sessions": len(user_sessions),
            "total_analyses": total_analyses,
            "onboarding_completed": any(
                s.get("metadata", {}).get("onboarding_completed", False) 
                for s in user_sessions
            )
        }


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
