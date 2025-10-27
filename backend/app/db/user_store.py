from datetime import datetime
from app.db.mongo_client import get_database
from app.models.profile_model import (
    UserDocument, ProfileCore, Medical, Nutrition, Goals, 
    MedicalHistory, BirthControl, Treatment, Preferences, 
    ReligiousRestrictions, Misc
)


async def create_user_document(user_id: str, slots: dict) -> dict:
    """
    Met à jour le profil nutritionnel d'un utilisateur existant (après onboarding).
    NE crée PAS un nouvel utilisateur - l'utilisateur doit avoir été créé lors de l'inscription.
    
    Args:
        user_id: ID de l'utilisateur existant
        slots: dictionnaire contenant les réponses d'onboarding (clés: slot names)
    
    Returns:
        Le document utilisateur mis à jour (avec profil complet)
    """
    db = await get_database()
    users_collection = db["user"]  # Collection 'user' au singulier
    
    # Vérifier que l'utilisateur existe
    existing_user = await users_collection.find_one({"user_id": user_id})
    if not existing_user:
        raise ValueError(f"Utilisateur {user_id} n'existe pas. Inscription requise avant l'onboarding.")
    
    # Construire le ProfileCore depuis les slots
    # Récupérer les informations existantes du profil (email, firstName, lastName)
    existing_profile = existing_user.get("profile", {})
    user_email = existing_profile.get("email", "")
    user_first_name = slots.get("firstName") or existing_profile.get("firstName", "")
    user_last_name = slots.get("lastName") or existing_profile.get("lastName", "")
    
    # Validation : l'email ne doit jamais être vide (contrainte d'unicité dans MongoDB)
    if not user_email:
        raise ValueError(f"Email manquant pour l'utilisateur {user_id}. Le profil doit avoir un email.")
    
    profile = ProfileCore(
        lastName=user_last_name,
        firstName=user_first_name,
        email=user_email,  # Récupérer l'email de l'utilisateur existant depuis profile.email
        age=int(slots.get("age", 0)) if slots.get("age") else 0,
        gender=slots.get("gender", "Other"),
        weight=float(slots.get("weight_kg", 0)) if slots.get("weight_kg") else 0.0,
        height=float(slots.get("height_cm", 0)) if slots.get("height_cm") else 0.0,
        bodyType=slots.get("bodyType", "unknown")
    )
    
    # Construire les autres sections
    medical = Medical(
        treatments=[
            Treatment(
                name=t.get("name"),
                dosage=t.get("dosage"),
                condition=t.get("condition")
            )
            for t in slots.get("treatments", [])
        ],
        allergies=slots.get("allergies", []),
        medicalHistory=MedicalHistory(
            personal=slots.get("medicalHistory_personal", []),
            family=slots.get("medicalHistory_family", [])
        ),
        birthControl=BirthControl(
            uses=slots.get("birthControl_uses", False),
            name=slots.get("birthControl_name")
        ) if slots.get("birthControl_uses") else None
    )
    
    nutrition = Nutrition(
        diet=slots.get("diet"),
        intolerances=slots.get("intolerances", []),
        preferences=Preferences(
            liked=slots.get("preferences_liked", []),
            disliked=slots.get("preferences_disliked", []),
            general=slots.get("preferences_general", [])
        )
    )
    
    goals = Goals(
        muscleGain=slots.get("muscleGain", False),
        weightLoss=slots.get("weightLoss", False),
        goalDetail=slots.get("goalDetail"),
        performance=slots.get("performance", False),
        maintainShape=slots.get("maintainShape", False)
    )
    
    religious = ReligiousRestrictions(
        practicing=slots.get("religiousRestrictions_practicing", False),
        type=slots.get("religiousRestrictions_type")
    ) if slots.get("religiousRestrictions_practicing") else None
    
    misc = Misc(
        activityLevel=slots.get("activityLevel"),
        sports=slots.get("sports", []),
        occupation=slots.get("occupation"),
        notes=slots.get("notes")
    )
    
    # Préparer les mises à jour (NE PAS écraser email, username, password_hash)
    profile_updates = {
        "profile": profile.model_dump(by_alias=True, exclude_none=False),
        "medical": medical.model_dump(by_alias=True, exclude_none=False),
        "nutrition": nutrition.model_dump(by_alias=True, exclude_none=False),
        "goals": goals.model_dump(by_alias=True, exclude_none=False),
        "religiousRestrictions": religious.model_dump(by_alias=True, exclude_none=False) if religious else None,
        "misc": misc.model_dump(by_alias=True, exclude_none=False) if misc else None,
        "profile_completed": True,
        "createdAt": datetime.utcnow()  # Rétrocompatibilité
    }
    
    # Mettre à jour uniquement les champs de profil (pas les champs d'auth)
    result = await users_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": profile_updates},
        return_document=True
    )
    
    if result:
        result["_id"] = str(result["_id"])
    
    return result


async def get_user_document(user_id: str) -> dict | None:
    """
    Récupère le UserDocument d'un utilisateur.
    """
    db = await get_database()
    users_collection = db["user"]  # Collection 'user' au singulier
    
    user = await users_collection.find_one({"user_id": user_id})
    return user


async def update_user_document(user_id: str, updates: dict) -> dict | None:
    """
    Met à jour le UserDocument d'un utilisateur.
    """
    db = await get_database()
    users_collection = db["user"]  # Collection 'user' au singulier
    
    result = await users_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": updates},
        return_document=True
    )
    return result