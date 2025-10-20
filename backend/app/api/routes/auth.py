"""
Routes pour l'authentification des utilisateurs.
Gestion de l'inscription et de la connexion.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import hashlib
import secrets

from app.db.mongo_client import get_database
from app.middleware.session_manager import SessionManager

router = APIRouter()


class RegisterRequest(BaseModel):
    """Requête d'inscription."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=3, max_length=50)


class LoginRequest(BaseModel):
    """Requête de connexion."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Réponse d'authentification."""
    success: bool
    message: str
    session_token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA256 + salt."""
    salt = "nutrition_app_salt_2025"  # En production, utiliser un salt unique par utilisateur
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Inscription d'un nouvel utilisateur.
    
    - **email**: Email de l'utilisateur (unique)
    - **password**: Mot de passe (minimum 6 caractères)
    - **username**: Nom d'utilisateur (3-50 caractères)
    
    Returns:
        AuthResponse avec session_token si succès
        
    Example:
        ```json
        POST /api/auth/register
        {
            "email": "alice@example.com",
            "password": "monMotDePasse123",
            "username": "Alice"
        }
        ```
    """
    db = await get_database()
    users = db["users"]
    
    # Vérifier si l'email existe déjà
    existing_user = await users.find_one({"email": request.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Vérifier si le username existe déjà
    existing_username = await users.find_one({"username": request.username})
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # Créer l'utilisateur
    user_id = f"user_{secrets.token_hex(8)}"
    user_data = {
        "user_id": user_id,
        "email": request.email.lower(),
        "username": request.username,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now(),
        "last_login": datetime.now(),
        "profile_completed": False
    }
    
    await users.insert_one(user_data)
    
    # Créer une session automatiquement
    session = await SessionManager.create_user_session(user_id)
    
    return AuthResponse(
        success=True,
        message="Inscription réussie ! Vous êtes maintenant connecté.",
        session_token=session["session_token"],
        user_id=user_id,
        username=request.username,
        email=request.email
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
            "email": "alice@example.com",
            "password": "monMotDePasse123"
        }
        ```
    """
    db = await get_database()
    users = db["users"]
    
    # Chercher l'utilisateur
    user = await users.find_one({"email": request.email.lower()})
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    # Vérifier le mot de passe
    password_hash = hash_password(request.password)
    if password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=401,
            detail="Email ou mot de passe incorrect"
        )
    
    # Mettre à jour la date de dernière connexion
    await users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": datetime.now()}}
    )
    
    # Créer une nouvelle session
    session = await SessionManager.create_user_session(user["user_id"])
    
    return AuthResponse(
        success=True,
        message="Connexion réussie !",
        session_token=session["session_token"],
        user_id=user["user_id"],
        username=user["username"],
        email=user["email"]
    )


@router.get("/check-email/{email}")
async def check_email(email: str):
    """
    Vérifie si un email est déjà utilisé.
    
    - **email**: Email à vérifier
    
    Returns:
        {"available": true/false}
    """
    db = await get_database()
    users = db["users"]
    
    existing_user = await users.find_one({"email": email.lower()})
    
    return {
        "email": email,
        "available": existing_user is None
    }


@router.get("/check-username/{username}")
async def check_username(username: str):
    """
    Vérifie si un nom d'utilisateur est déjà pris.
    
    - **username**: Nom d'utilisateur à vérifier
    
    Returns:
        {"available": true/false}
    """
    db = await get_database()
    users = db["users"]
    
    existing_user = await users.find_one({"username": username})
    
    return {
        "username": username,
        "available": existing_user is None
    }
