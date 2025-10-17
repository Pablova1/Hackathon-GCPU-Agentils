from datetime import datetime
from app.db.mongo_client import get_database
from app.models.profile_model import UserDocument

# Fonction d’enregistrement du profil utilisateur
async def save_user_profile(data: UserDocument) -> str:
    """
    Valide et enregistre un profil utilisateur dans la collection 'user'.
    Génère automatiquement un _id MongoDB si absent.
    """
    # Connexion à la base
    db = await get_database()
    profiles_collection = db["user"]

    # Ajouter la date de création si absente
    if not data.createdAt:
        data.createdAt = datetime.utcnow()

    # Convertir le modèle Pydantic en dictionnaire Mongo-compatible
    # by_alias=True → garde le nom "_id" si défini
    # exclude_none=True → évite d’insérer les valeurs nulles
    document = data.model_dump(by_alias=True, exclude_none=True)

    # Insertion du document dans MongoDB
    result = await profiles_collection.insert_one(document)

    # Retourner l’identifiant inséré sous forme de chaîne
    return str(result.inserted_id)


