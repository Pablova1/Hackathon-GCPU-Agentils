"""
Store pour gérer les opérations CRUD sur la collection 'meals'
"""
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.db.mongo_client import get_database
from app.models.meal_model import MealDocument, MealCreate, MealUpdate, Nutrients


async def create_meal(meal_data: MealCreate) -> dict:
    """
    Crée un nouveau repas dans la base de données.
    
    Args:
        meal_data: Données du repas à créer
    
    Returns:
        Le document du repas créé avec son _id MongoDB
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    # Préparer le document à insérer
    meal_dict = {
        "userId": meal_data.userId,
        "name": meal_data.name,
        "ingredients": meal_data.ingredients,
        "nutrients": meal_data.nutrients.model_dump() if meal_data.nutrients else {},
        "dateScanned": datetime.utcnow()
    }
    
    # Insérer dans MongoDB
    result = await meals_collection.insert_one(meal_dict)
    
    # Récupérer le document créé
    created_meal = await meals_collection.find_one({"_id": result.inserted_id})
    
    return created_meal


async def get_meal_by_id(meal_id: str) -> Optional[dict]:
    """
    Récupère un repas par son ID.
    
    Args:
        meal_id: ID du repas
    
    Returns:
        Le document du repas ou None si non trouvé
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    try:
        meal = await meals_collection.find_one({"_id": ObjectId(meal_id)})
        return meal
    except Exception:
        return None


async def get_meals_by_user_id(user_id: str, limit: int = 100, skip: int = 0) -> List[dict]:
    """
    Récupère tous les repas d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        limit: Nombre maximum de résultats
        skip: Nombre de résultats à sauter (pour la pagination)
    
    Returns:
        Liste des repas de l'utilisateur
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    cursor = meals_collection.find({"userId": user_id}) \
        .sort("dateScanned", -1) \
        .skip(skip) \
        .limit(limit)
    
    meals = await cursor.to_list(length=limit)
    return meals


async def get_meals_by_date_range(
    user_id: str,
    start_date: datetime,
    end_date: datetime
) -> List[dict]:
    """
    Récupère les repas d'un utilisateur dans une plage de dates.
    
    Args:
        user_id: ID de l'utilisateur
        start_date: Date de début
        end_date: Date de fin
    
    Returns:
        Liste des repas dans la plage de dates
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    cursor = meals_collection.find({
        "userId": user_id,
        "dateScanned": {
            "$gte": start_date,
            "$lte": end_date
        }
    }).sort("dateScanned", -1)
    
    meals = await cursor.to_list(length=None)
    return meals


async def update_meal(meal_id: str, meal_update: MealUpdate) -> Optional[dict]:
    """
    Met à jour un repas existant.
    
    Args:
        meal_id: ID du repas à mettre à jour
        meal_update: Données de mise à jour
    
    Returns:
        Le document du repas mis à jour ou None si non trouvé
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    # Préparer les données de mise à jour (exclure les None)
    update_data = meal_update.model_dump(exclude_none=True)
    
    # Convertir l'objet Nutrients en dict si présent
    if "nutrients" in update_data and update_data["nutrients"]:
        update_data["nutrients"] = update_data["nutrients"]
    
    if not update_data:
        return await get_meal_by_id(meal_id)
    
    try:
        result = await meals_collection.find_one_and_update(
            {"_id": ObjectId(meal_id)},
            {"$set": update_data},
            return_document=True
        )
        return result
    except Exception:
        return None


async def delete_meal(meal_id: str) -> bool:
    """
    Supprime un repas.
    
    Args:
        meal_id: ID du repas à supprimer
    
    Returns:
        True si le repas a été supprimé, False sinon
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    try:
        result = await meals_collection.delete_one({"_id": ObjectId(meal_id)})
        return result.deleted_count > 0
    except Exception:
        return False


async def delete_user_meals(user_id: str) -> int:
    """
    Supprime tous les repas d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Nombre de repas supprimés
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    result = await meals_collection.delete_many({"userId": user_id})
    return result.deleted_count


async def count_user_meals(user_id: str) -> int:
    """
    Compte le nombre de repas d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Nombre de repas
    """
    db = await get_database()
    meals_collection = db["meals"]
    
    count = await meals_collection.count_documents({"userId": user_id})
    return count
