"""
Routes API pour la gestion des repas (meals)
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.models.meal_model import MealDocument, MealCreate, MealUpdate
from app.db.meal_store import (
    create_meal,
    get_meal_by_id,
    get_meals_by_user_id,
    get_meals_by_date_range,
    update_meal,
    delete_meal,
    delete_user_meals,
    count_user_meals,
    get_monthly_calendar,
    get_home_stats,
    get_weekly_meals
)

router = APIRouter(prefix="/meals", tags=["meals"])


# ─────────────────────────────────────────────────────────────
# Schémas de réponse
# ─────────────────────────────────────────────────────────────

class MealResponse(BaseModel):
    """Réponse contenant un repas"""
    _id: str
    userId: str
    name: str
    ingredients: List[str]
    nutrients: dict
    dateScanned: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "68efab5a4b0f91f9f00c3196",
                "userId": "68efa5944b0f91f9f00c318d",
                "name": "Healthy Chicken Bowl",
                "ingredients": ["chicken breast", "quinoa", "broccoli"],
                "nutrients": {
                    "calories": 450.5,
                    "protein": 35.2,
                    "fat": 12.8,
                    "carbohydrates": 45.3,
                    "fiber": 8.5
                },
                "dateScanned": "2025-01-15T12:30:00Z"
            }
        }


class MealsListResponse(BaseModel):
    """Réponse contenant une liste de repas"""
    meals: List[MealResponse]
    total: int
    skip: int
    limit: int


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=MealResponse, status_code=201)
async def create_new_meal(meal_data: MealCreate):
    """
    Crée un nouveau repas.
    
    - **userId**: ID de l'utilisateur
    - **name**: Nom du repas (optionnel)
    - **ingredients**: Liste des ingrédients
    - **nutrients**: Informations nutritionnelles
    """
    try:
        meal = await create_meal(meal_data)
        if not meal:
            raise HTTPException(status_code=500, detail="Erreur lors de la création du repas")
        
        # Convertir ObjectId en string pour la réponse
        meal["_id"] = str(meal["_id"])
        return meal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal(meal_id: str):
    """
    Récupère un repas par son ID.
    
    - **meal_id**: ID du repas
    """
    meal = await get_meal_by_id(meal_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Repas non trouvé")
    
    meal["_id"] = str(meal["_id"])
    return meal


@router.get("/user/{user_id}", response_model=MealsListResponse)
async def get_user_meals(
    user_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    skip: int = Query(default=0, ge=0)
):
    """
    Récupère tous les repas d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    - **limit**: Nombre maximum de résultats (défaut: 100)
    - **skip**: Nombre de résultats à sauter pour la pagination (défaut: 0)
    """
    try:
        meals = await get_meals_by_user_id(user_id, limit=limit, skip=skip)
        total = await count_user_meals(user_id)
        
        # Convertir ObjectId en string
        for meal in meals:
            meal["_id"] = str(meal["_id"])
        
        return {
            "meals": meals,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/user/{user_id}/range")
async def get_user_meals_by_range(
    user_id: str,
    start_date: datetime = Query(..., description="Date de début (ISO format)"),
    end_date: datetime = Query(..., description="Date de fin (ISO format)")
):
    """
    Récupère les repas d'un utilisateur dans une plage de dates.
    
    - **user_id**: ID de l'utilisateur
    - **start_date**: Date de début (format ISO: 2025-01-01T00:00:00Z)
    - **end_date**: Date de fin (format ISO: 2025-01-31T23:59:59Z)
    """
    try:
        meals = await get_meals_by_date_range(user_id, start_date, end_date)
        
        # Convertir ObjectId en string
        for meal in meals:
            meal["_id"] = str(meal["_id"])
        
        return {
            "meals": meals,
            "total": len(meals),
            "start_date": start_date,
            "end_date": end_date
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.put("/{meal_id}", response_model=MealResponse)
async def update_existing_meal(meal_id: str, meal_update: MealUpdate):
    """
    Met à jour un repas existant.
    
    - **meal_id**: ID du repas
    - **meal_update**: Données à mettre à jour (tous les champs sont optionnels)
    """
    meal = await update_meal(meal_id, meal_update)
    if not meal:
        raise HTTPException(status_code=404, detail="Repas non trouvé")
    
    meal["_id"] = str(meal["_id"])
    return meal


@router.delete("/{meal_id}")
async def delete_existing_meal(meal_id: str):
    """
    Supprime un repas.
    
    - **meal_id**: ID du repas à supprimer
    """
    success = await delete_meal(meal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Repas non trouvé")
    
    return {"message": "Repas supprimé avec succès"}


@router.delete("/user/{user_id}/all")
async def delete_all_user_meals(user_id: str):
    """
    Supprime tous les repas d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    """
    try:
        deleted_count = await delete_user_meals(user_id)
        return {
            "message": f"{deleted_count} repas supprimé(s) avec succès",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/user/{user_id}/count")
async def get_user_meals_count(user_id: str):
    """
    Compte le nombre de repas d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    """
    try:
        count = await count_user_meals(user_id)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/user/{user_id}/monthly-calendar")
async def get_user_monthly_calendar(
    user_id: str,
    year: int = Query(..., description="Année (ex: 2025)"),
    month: int = Query(..., ge=1, le=12, description="Mois (1-12)")
):
    """
    Récupère le calendrier mensuel avec les jours où des plats ont été scannés.
    
    - **user_id**: ID de l'utilisateur
    - **year**: Année (ex: 2025)
    - **month**: Mois (1-12)
    
    Retourne:
    - **year**: année
    - **month**: mois
    - **days_with_meals**: liste des jours où au moins un plat a été scanné
    - **total_meals_in_month**: nombre total de plats scannés ce mois
    """
    try:
        calendar_data = await get_monthly_calendar(user_id, year, month)
        return calendar_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/user/{user_id}/home-stats")
async def get_user_home_stats(user_id: str):
    """
    Récupère les statistiques pour la page d'accueil.
    
    - **user_id**: ID de l'utilisateur
    
    Retourne:
    - **total_meals_scanned**: nombre total de plats scannés
    - **current_month_calendar**: calendrier du mois en cours avec les jours où des plats ont été scannés
    - **weekly_score**: note hebdomadaire (1-5) calculée par l'IA avec un commentaire
        - score: note entre 1 et 5
        - comment: commentaire encourageant de l'IA
    """
    try:
        stats = await get_home_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.get("/user/{user_id}/weekly-score")
async def get_user_weekly_score(user_id: str):
    """
    Calcule la note hebdomadaire basée sur les plats scannés durant les 7 derniers jours.
    
    - **user_id**: ID de l'utilisateur
    
    Retourne:
    - **score**: note entre 1 et 5
    - **comment**: commentaire encourageant de l'IA nutritionniste
    - **meals_count**: nombre de repas analysés dans la semaine
    """
    try:
        from app.ai.homepage_ai import calculate_weekly_score
        
        weekly_meals = await get_weekly_meals(user_id)
        weekly_score = calculate_weekly_score(weekly_meals)
        
        if weekly_score is None:
            raise HTTPException(status_code=500, detail="Erreur lors du calcul de la note")
        
        return {
            **weekly_score,
            "meals_count": len(weekly_meals)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")



