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
    lastName: str
    firstName: str
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
    id: Optional[str] = Field(default=None, alias="_id")
    profile: ProfileCore
    medical: Medical
    nutrition: Nutrition
    goals: Goals
    religiousRestrictions: Optional[ReligiousRestrictions] = None
    misc: Optional[Misc] = None
    createdAt: datetime

    model_config = dict(
        populate_by_name=True,
        extra="ignore"
    )
