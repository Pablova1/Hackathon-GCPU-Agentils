from __future__ import annotations
from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────
# Sous-modèles
# ─────────────────────────────────────────────────────────────

Gender = Literal["Male", "Female", "Other"]
BodyType = Literal["ectomorphic", "mesomorphic", "endomorphic", "unknown"]
ActivityLevel = Literal["low", "moderate", "high"]

class Treatment(BaseModel):
    name: str
    dosage: Optional[str] = None
    condition: Optional[str] = None

class MedicalHistory(BaseModel):
    personal: List[str] = []
    family: List[str] = []

class BirthControl(BaseModel):
    uses: bool
    name: Optional[str] = None

class Medical(BaseModel):
    treatments: List[Treatment] = []
    allergies: List[str] = []
    medicalHistory: MedicalHistory = MedicalHistory()
    birthControl: Optional[BirthControl] = None

class Preferences(BaseModel):
    liked: List[str] = []      
    disliked: List[str] = []    
    general: List[str] = []     

class Nutrition(BaseModel):
    diet: Optional[str] = None
    intolerances: List[str] = []
    preferences: Preferences = Preferences()

class Goals(BaseModel):
    muscleGain: bool = False
    weightLoss: bool = False
    goalDetail: Optional[str] = None
    performance: bool = False
    maintainShape: bool = False

class ProfileCore(BaseModel):
    """Informations de profil de base de l'utilisateur."""
    firstName: str
    lastName: str
    email: str  # Email de l'utilisateur (unique)
    age: int = Field(ge=0, le=130)
    gender: Gender
    weight: float = Field(ge=0)
    height: float = Field(ge=0)
    bodyType: Optional[BodyType] = "unknown"

class ReligiousRestrictions(BaseModel):
    practicing: bool = False
    type: Optional[str] = None

class Misc(BaseModel):
    activityLevel: Optional[ActivityLevel] = None
    sports: List[str] = []
    occupation: Optional[str] = None
    notes: Optional[str] = None

# ─────────────────────────────────────────────────────────────
# Document principal (comme en Mongo)
# ─────────────────────────────────────────────────────────────

class UserDocument(BaseModel):
    """
    Document utilisateur complet stocké dans MongoDB (collection 'user').
    Contient à la fois les informations d'authentification et le profil nutritionnel.
    
    Structure:
    - user_id: Identifiant unique système
    - password_hash: Authentification
    - profile: Contient firstName, lastName, email, age, gender, weight, height, bodyType
    - medical: Allergies, traitements, historique médical
    - nutrition: Régime alimentaire, intolérances, préférences
    - goals: Objectifs (perte de poids, gain musculaire, etc.)
    - religiousRestrictions: Restrictions religieuses
    - misc: Niveau d'activité, sports, occupation, notes
    - created_at, profile_completed: Métadonnées
    """
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str  # Identifiant unique de l'utilisateur (ex: user_abc123)
    
    # Authentification
    password_hash: str  # Hash SHA256 du mot de passe
    
    # Profil (contient maintenant l'email)
    profile: Optional[ProfileCore] = None
    
    # Santé et nutrition
    medical: Optional[Medical] = None
    nutrition: Optional[Nutrition] = None
    goals: Optional[Goals] = None
    religiousRestrictions: Optional[ReligiousRestrictions] = None
    misc: Optional[Misc] = None
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    profile_completed: bool = False  # True après l'onboarding
    createdAt: Optional[datetime] = None  # Rétrocompatibilité
    
    # Session (remplace la collection user_sessions)
    session_token: Optional[str] = None  # Token de session actif
    session_created_at: Optional[datetime] = None  # Date de création de la session
    session_expires_at: Optional[datetime] = None  # Date d'expiration de la session
    last_activity: Optional[datetime] = None  # Dernière activité de l'utilisateur

    model_config = dict(
        populate_by_name=True,
        extra="ignore"
    )
