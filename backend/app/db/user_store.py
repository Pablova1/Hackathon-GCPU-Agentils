from datetime import datetime
from app.db.mongo_client import get_database
from app.models.user import (
    UserDocument, ProfileCore, Medical, Nutrition, Goals, 
    MedicalHistory, BirthControl, Treatment, Preferences, 
    ReligiousRestrictions, Misc
)


async def create_user_document(user_id: str, slots: dict) -> dict:
    """
    Crée un UserDocument à partir des slots d'onboarding.
    Sauvegarde dans MongoDB et retourne le document créé.
    
    Args:
        user_id: ID de l'utilisateur
        slots: dictionnaire contenant les réponses (clés: slot names)
    
    Returns:
        Le document utilisateur créé (avec _id MongoDB)
    """
    db = await get_database()
    users_collection = db["user"]  # Collection 'user' au singulier
    
    # Construire le ProfileCore depuis les slots
    profile = ProfileCore(
        lastName=slots.get("lastName", ""),
        firstName=slots.get("firstName", ""),
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
    
    # Créer le UserDocument
    user_doc = UserDocument(
        profile=profile,
        medical=medical,
        nutrition=nutrition,
        goals=goals,
        religiousRestrictions=religious,
        misc=misc,
        createdAt=datetime.utcnow()
    )
    
    # Convertir en dict pour MongoDB - EXCLURE _id car MongoDB le génère automatiquement
    doc_dict = user_doc.model_dump(
        by_alias=True,
        exclude_none=False,
        exclude_unset=False,
        exclude={"id"}  # Exclure le champ id/_id pour éviter l'erreur de clé dupliquée
    )
    
    # Ajouter l'user_id
    doc_dict["user_id"] = user_id
    
    # Insérer dans MongoDB
    result = await users_collection.insert_one(doc_dict)
    doc_dict["_id"] = str(result.inserted_id)
    
    return doc_dict


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