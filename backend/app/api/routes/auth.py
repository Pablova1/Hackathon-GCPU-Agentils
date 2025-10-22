"""
Routes pour l'authentification des utilisateurs.
Gestion de l'inscription et de la connexion.

NOUVEAU SCHÉMA:
- Email stocké dans profile.email (avec firstName, lastName)
- Pas de username (redondant avec prénom + nom)
- password_hash à la racine du document
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import secrets

from app.db.mongo_client import get_database
from app.middleware.session_manager import SessionManager

router = APIRouter()


class RegisterRequest(BaseModel):
    """Requête d'inscription."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)


class LoginRequest(BaseModel):
    """Requête de connexion."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Réponse d'authentification."""
    success: bool = True
    message: Optional[str] = None
    session_token: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


def hash_password(password: str, user_id: str) -> str:
    """Hash un mot de passe avec SHA256 + user_id comme salt."""
    return hashlib.sha256(f"{password}{user_id}".encode()).hexdigest()


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Inscription d'un nouvel utilisateur.
    
    - **email**: Email de l'utilisateur (unique)
    - **password**: Mot de passe (minimum 6 caractères)
    - **first_name**: Prénom de l'utilisateur
    - **last_name**: Nom de famille de l'utilisateur
    
    Returns:
        AuthResponse avec session_token si succès
        
    Example:
        ```json
        POST /api/auth/register
        {
            "email": "alice.martin@example.com",
            "password": "monMotDePasse123",
            "first_name": "Alice",
            "last_name": "Martin"
        }
        ```
    """
    db = await get_database()
    users = db["user"]
    
    # Vérifier si l'email existe déjà (chercher dans profile.email)
    existing_user = await users.find_one({"profile.email": request.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer l'utilisateur avec un token de session initial
    user_id = f"user_{secrets.token_hex(8)}"
    session_token = str(secrets.token_urlsafe(32))
    now = datetime.now()
    
    user_data = {
        "user_id": user_id,
        "password_hash": hash_password(request.password, user_id),
        "created_at": now,
        "last_login": now,
        "profile_completed": False,
        
        # Session intégrée dans le document user
        "session_token": session_token,
        "session_created_at": now,
        "session_expires_at": now + timedelta(hours=24),
        "last_activity": now,
        
        # Profil de base avec email, prénom, nom
        "profile": {
            "firstName": request.first_name,
            "lastName": request.last_name,
            "email": request.email.lower(),
            # Les autres champs seront remplis lors de l'onboarding
            "age": 0,
            "gender": "Other",
            "weight": 0.0,
            "height": 0.0,
            "bodyType": "unknown"
        },
        
        # Les autres sections seront remplies lors de l'onboarding
        "medical": None,
        "nutrition": None,
        "goals": None,
        "religiousRestrictions": None,
        "misc": None
    }
    
    result = await users.insert_one(user_data)
    
    return AuthResponse(
        success=True,
        message="Compte créé avec succès",
        session_token=session_token,
        user_id=user_id,
        email=request.email.lower(),
        first_name=request.first_name,
        last_name=request.last_name
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Connexion d'un utilisateur existant.
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    
    Returns:
        AuthResponse avec session_token si succès
        
    Example:
        ```json
        POST /api/auth/login
        {
            "email": "alice.martin@example.com",
            "password": "monMotDePasse123"
        }
        ```
    """
    db = await get_database()
    users = db["user"]
    
    # Chercher l'utilisateur par email (dans profile.email OU à la racine pour compatibilité)
    user = await users.find_one({
        "$or": [
            {"profile.email": request.email.lower()},
            {"email": request.email.lower()}  # Fallback pour anciens utilisateurs
        ]
    })
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier le mot de passe
    user_id = user.get("user_id")
    password_hash = hash_password(request.password, user_id)
    
    if password_hash != user.get("password_hash"):
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    # Créer une nouvelle session
    session_manager = SessionManager()
    session_data = await session_manager.create_user_session(user_id)
    
    # Récupérer les informations du profil
    profile = user.get("profile", {})
    first_name = profile.get("firstName", "User")
    last_name = profile.get("lastName", "")
    email = profile.get("email", user.get("email", ""))  # Fallback
    
    return AuthResponse(
        success=True,
        message="Connexion réussie",
        session_token=session_data["session_token"],
        user_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name
    )


@router.get("/check-email/{email}")
async def check_email(email: str):
    """
    Vérifie si un email est disponible.
    
    Returns:
        {"available": true/false}
    """
    db = await get_database()
    users = db["user"]
    
    existing_user = await users.find_one({"profile.email": email.lower()})
    
    return {
        "available": existing_user is None,
        "message": "Email disponible" if existing_user is None else "Email déjà utilisé"
    }


@router.post("/logout")
async def logout(session_token: str):
    """
    Déconnexion - Révoque la session côté serveur.
    
    Args:
        session_token: Token de session à révoquer
    """
    db = await get_database()
    users = db["user"]
    
    # Supprimer le token de session de l'utilisateur
    await users.update_one(
        {"session_token": session_token},
        {
            "$unset": {
                "session_token": "",
                "session_created_at": "",
                "session_expires_at": ""
            }
        }
    )
    
    return {
        "success": True,
        "message": "Déconnexion réussie"
    }
