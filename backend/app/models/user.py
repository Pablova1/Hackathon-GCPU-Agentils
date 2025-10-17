"""
Modèles pour les documents utilisateurs - copie de profile_model.py pour compatibilité
"""
from app.models.profile_model import (
    UserDocument,
    ProfileCore,
    Medical,
    Nutrition,
    Goals,
    MedicalHistory,
    BirthControl,
    Treatment,
    Preferences,
    ReligiousRestrictions,
    Misc,
    Gender,
    BodyType,
    ActivityLevel
)

__all__ = [
    "UserDocument",
    "ProfileCore",
    "Medical",
    "Nutrition",
    "Goals",
    "MedicalHistory",
    "BirthControl",
    "Treatment",
    "Preferences",
    "ReligiousRestrictions",
    "Misc",
    "Gender",
    "BodyType",
    "ActivityLevel"
]
