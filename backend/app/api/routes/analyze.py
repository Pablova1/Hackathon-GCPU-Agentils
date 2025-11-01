"""
Routes pour l'analyse d'assiettes.
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import shutil
from pathlib import Path
import logging
import uuid
from datetime import datetime
import json

# Google ADK imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App
from google.genai import types

# App imports
from app.core.config import settings
from app.middleware.session_manager import get_current_session, get_optional_session, SessionManager
from app.db.mongo_client import get_database
from app.adk.agent_registry import get_plate_analyzer_agent, get_nutriment_analyzer_agent
from app.adk.image_agent.plate_analyze.agent import AlimentQuantite

logger = logging.getLogger(__name__)

# Création du router unique
router = APIRouter()


@router.post("/plate")
async def analyze_plate(
    file: UploadFile = File(...),
    session: dict = Depends(get_current_session)
):
    """
    Analyse une image d'assiette et retourne les aliments détectés.
    **Authentification requise** : Header `X-Session-Token`
    """
    user_id = session["user_id"]
    session_token = session["session_token"]
    
    # Vérification du type de fichier
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non supporté. Types acceptés: {', '.join(allowed_types)}"
        )
    
    # Lecture du contenu de l'image
    image_bytes = await file.read()
    
    logger.info(f"Analyse d'image pour user {user_id}")
    
    # Récupération de l'agent
    plate_analyzer_agent = get_plate_analyzer_agent()
    
    # Crée une app contenant ton agent
    app = App(name="meal_agent_app", root_agent=plate_analyzer_agent) 
    
    # Create session service and runner
    session_service = InMemorySessionService()
    app_name = "meal_agent_app"
    session_id = f"meal_session_{user_id}"
    
    # Create session
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    # Create runner
    runner = Runner(
        agent=plate_analyzer_agent,
        app_name=app_name,
        session_service=session_service
    )
    
    # Créer un message avec l'image
    message = types.Content(
        role="user",
        parts=[
            types.Part(
                inline_data={
                    "mime_type": file.content_type,
                    "data": image_bytes
                }
            )
        ]
    )
    
    # Lancer l'appel à l'agent avec l'image
    try:
        events = runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        )
        
        # Consommer tous les événements du générateur
        for event in events:
            pass
            
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse pour user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
    
    # Récupération de la réponse structurée
    session_data = await session_service.get_session(
        user_id=user_id, 
        session_id=session_id,
        app_name=app_name
    )
    
    plate_result = session_data.state.get("plate_analysis_result")
    
    if not plate_result:
        raise HTTPException(status_code=500, detail="Aucune donnée d'analyse trouvée.")
    
    # Extraction et formatage des aliments
    aliments_raw = plate_result.get("foods", [])
    
    # Convertir au format attendu par le front (name + estimated_quantity)
    aliments = []
    for item in aliments_raw:
        aliments.append({
            "name": item.get("aliment", item.get("name", "")),
            "estimated_quantity": int(item.get("quantite", item.get("estimated_quantity", 0)))
        })
    logger.info(f"Aliments détectés: {aliments}")
    
    
    # Formatage de la réponse (même format que l'ancienne API)
    response = {
        "success": True,
        "aliments": aliments,
        "nombre_aliments": len(aliments),
        "message": f"{len(aliments)} aliment(s) détecté(s)"
    }
    
    logger.info(f"✅ Analyse réussie pour user {user_id}: {response['nombre_aliments']} aliments")
    
    return response

#=
# Section : Analyse nutritionnelle avec ADK

class AlimentInput(BaseModel):
    name: str  # Le front envoie "name"
    estimated_quantity: int  # Le front envoie "estimated_quantity"
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Chicken",
                "estimated_quantity": 150
            }
        }

class AnalyzeNutrientsRequest(BaseModel):
    aliments: List[AlimentInput]

@router.post("/nutrients")
async def analyze_nutrients(
    aliments: List[AlimentInput],  # Directement une liste, pas un objet wrapper
    background_tasks: BackgroundTasks,
    session: dict = Depends(get_current_session)
):
    """
    Analyse les nutriments pour une liste d'aliments.
    Déclenche automatiquement la génération de suggestions en arrière-plan.
    
    **Authentification requise** : Vous devez fournir un header `X-Session-Token`.

    - **aliments**: Liste des aliments avec leur nom et quantité estimée.
    
    Headers:
        - X-Session-Token: Token de session valide
    """
    try:
        user_id = session["user_id"]
        session_token = session["session_token"]
        
        # Log the raw aliments for debugging
        logger.info(f"Raw aliments received from user {user_id}: {jsonable_encoder(aliments)}")

        # Conversion des aliments pour l'agent ADK
        aliments_data = [
            {"name": aliment.name, "estimated_quantity": aliment.estimated_quantity}
            for aliment in aliments
        ]

        # Log the structured aliments data
        logger.info(f"Structured aliments data: {aliments_data}")

        # Récupération de l'agent ADK
        from app.adk.agent_registry import get_nutriment_analyzer_agent
        nutriment_agent = get_nutriment_analyzer_agent()
        
        # Create app
        app = App(name="nutriment_app", root_agent=nutriment_agent)
        
        # Create session service
        session_service = InMemorySessionService()
        app_name = "nutriment_app"
        session_id = f"nutriment_session_{user_id}"
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=nutriment_agent,
            app_name=app_name,
            session_service=session_service
        )
        
        # Formater les aliments pour le message
        aliments_text = "Analyze the nutritional values for these foods:\n\n"
        for alim in aliments:
            aliments_text += f"- {alim.name}: {alim.estimated_quantity}g\n"
        
        aliments_text += "\nProvide complete nutritional information (macronutrients and micronutrients) for each food based on the specified quantity."
        
        # Créer le message
        message = types.Content(
            role="user",
            parts=[
                types.Part(text=aliments_text)
            ]
        )
        
        # Lancer l'analyse
        try:
            events = runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=message
            )
            
            # Consommer les événements
            for event in events:
                pass
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse nutritionnelle: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse : {str(e)}")
        
        # Récupérer le résultat
        session_data = await session_service.get_session(
            user_id=user_id,
            session_id=session_id,
            app_name=app_name
        )
        
        nutriment_result = session_data.state.get("nutriment_analysis_result")
        
        if not nutriment_result:
            raise HTTPException(status_code=500, detail="Aucune donnée nutritionnelle trouvée.")
        
        # Convertir le résultat ADK au format de l'ancienne API
        foods_nutrition = nutriment_result.get("foods_nutrition", [])

        # Reformater pour correspondre à l'ancien format attendu par calculate_nutrient_summary
        result = []
        for food in foods_nutrition:
            food_data = {
                "food": food["food"],
                "quantity": food["quantity"],
                "nutritional_values": food["nutritional_values"],
                "micronutrients": food["micronutrients"]
            }
            result.append(food_data)

        # Log the result
        logger.info(f"Nutrient analysis result: {result}")

        logger.info("=========On va faire la somme des nutriments=========")

        # Calculate nutrient summary manuellement au lieu d'appeler la fonction
        # car elle attend peut-être un format différent
        total_nutritional_values = {
            "energy_kcal": 0.0,
            "proteins_g": 0.0,
            "carbohydrates_g": 0.0,
            "lipids_g": 0.0,
            "fiber_g": 0.0,
            "sugars_g": 0.0,
            "saturated_fats_g": 0.0,
            "unsaturated_fats_g": 0.0
        }

        total_micronutrients = {
            "calcium_mg": 0.0,
            "iron_mg": 0.0,
            "magnesium_mg": 0.0,
            "potassium_mg": 0.0,
            "sodium_mg": 0.0,
            "zinc_mg": 0.0,
            "phosphorus_mg": 0.0,
            "vitamin_a_mcg": 0.0,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.0,
            "vitamin_e_mg": 0.0,
            "vitamin_b12_mcg": 0.0
        }

        # Sommer les nutriments
        for food in result:
            nutritional_values = food.get("nutritional_values", {})
            micronutrients = food.get("micronutrients", {})
            
            # Additionner les macronutriments
            for key in total_nutritional_values:
                total_nutritional_values[key] += nutritional_values.get(key, 0.0)
            
            # Additionner les micronutriments
            for key in total_micronutrients:
                total_micronutrients[key] += micronutrients.get(key, 0.0)

        # Créer le nutrient_summary au même format que l'ancienne API
        nutrient_summary = {
            "nutritional_values": total_nutritional_values,
            "micronutrients": total_micronutrients
        }

        # Log the nutrient summary
        logger.info(f"Nutrient summary: {nutrient_summary}")
                
        # 🆕 SAUVEGARDE de l'analyse nutritionnelle dans MongoDB
        db = await get_database()
        nutrient_analyses = db["nutrient_analyses"]
        
        nutrient_record = {
            "user_id": user_id,
            "session_token": session_token,
            "aliments": aliments_data,
            "nutrients": result,
            "nutrient_summary": nutrient_summary,
            "analyzed_at": datetime.now().isoformat()
        }
        
        await nutrient_analyses.insert_one(nutrient_record)
        logger.info(f"✅ Analyse nutritionnelle sauvegardée pour user {user_id}")

        # 🔥 JONCTION : Créer un repas dans la collection meals pour le scoring hebdomadaire
        from app.db.meal_store import create_meal
        from app.models.meal_model import MealCreate, Nutrients
        
        # Extraire les ingrédients depuis aliments_data
        ingredients = [aliment["name"] for aliment in aliments_data]
        
        # Créer l'objet Nutrients depuis le nutrient_summary
        nutritional_values = nutrient_summary.get("nutritional_values", {})
        
        meal_nutrients = Nutrients(
            calories=nutritional_values.get("energy_kcal", 0),
            protein=nutritional_values.get("proteins_g", 0),
            fat=nutritional_values.get("lipids_g", 0),
            carbohydrates=nutritional_values.get("carbohydrates_g", 0),
            fiber=nutritional_values.get("fiber_g", 0)
        )
        
        # Créer le repas
        meal_create = MealCreate(
            userId=user_id,
            name=f"Repas du {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            ingredients=ingredients,
            nutrients=meal_nutrients
        )
        
        created_meal = await create_meal(meal_create)
        logger.info(f"🍽️ Repas créé dans la collection meals avec ID: {created_meal['_id']}")

        # 🚀 NOUVEAU : Déclencher la génération de suggestions en arrière-plan
        from app.api.routes.suggestions import generate_and_store_suggestions
        background_tasks.add_task(generate_and_store_suggestions, user_id, 7)
        logger.info(f"🔄 Background suggestion generation triggered for user {user_id}")

        return {
            "success": True,
            "nutrients": result,
            "nutrient_summary": nutrient_summary,
            "meal_id": str(created_meal['_id']),
            "message": "Analyse des nutriments réussie et repas enregistré. Suggestions en cours de génération.",
            "suggestion_status": "generating"
        }

    except ValueError as e:
        logger.error(f"Erreur de parsing: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Erreur lors de l'analyse des nutriments: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des nutriments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne: {str(e)}"
        )














#=



@router.get("/health")
async def health_check():
    """Vérifie l'état des agents d'analyse."""
    try:
        food_analyzer = get_plate_analyzer_agent()
        nutrient_analyzer = get_nutriment_analyzer_agent()
        
        return {
            "status": "healthy",
            "agents": {
                "food_analyzer": {
                    "status": "ready",
                    "model": food_analyzer.model_name
                },
                "nutrient_analyzer": {
                    "status": "ready",
                    "model": nutrient_analyzer.model_name
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service indisponible: {str(e)}"
        )

@router.get("/history")
async def get_analysis_history(
    session: dict = Depends(get_current_session),
    limit: int = 10
):
    """
    Récupère l'historique des analyses d'assiettes pour l'utilisateur courant.
    
    **Authentification requise** : Vous devez fournir un header `X-Session-Token`.
    
    - **limit**: Nombre maximum de résultats (par défaut: 10)
    
    Headers:
        - X-Session-Token: Token de session valide
        
    Returns:
        Liste des analyses précédentes de l'utilisateur
    """
    user_id = session["user_id"]
    
    db = await get_database()
    analyses_collection = db["plate_analyses"]
    
    # Récupération des analyses de l'utilisateur
    cursor = analyses_collection.find(
        {"user_id": user_id}
    ).sort("analyzed_at", -1).limit(limit)
    
    analyses = await cursor.to_list(length=limit)
    
    # Nettoyage des résultats (retirer _id de MongoDB)
    for analysis in analyses:
        analysis.pop("_id", None)
    
    logger.info(f"📊 Historique récupéré pour user {user_id}: {len(analyses)} analyses")
    
    return {
        "user_id": user_id,
        "total": len(analyses),
        "analyses": analyses
    }


@router.get("/nutrients/history")
async def get_nutrient_history(
    session: dict = Depends(get_current_session),
    limit: int = 10
):
    """
    Récupère l'historique des analyses nutritionnelles pour l'utilisateur courant.
    
    **Authentification requise** : Vous devez fournir un header `X-Session-Token`.
    
    - **limit**: Nombre maximum de résultats (par défaut: 10)
    
    Headers:
        - X-Session-Token: Token de session valide
        
    Returns:
        Liste des analyses nutritionnelles précédentes de l'utilisateur
    """
    user_id = session["user_id"]
    
    db = await get_database()
    nutrient_analyses = db["nutrient_analyses"]
    
    # Récupération des analyses de l'utilisateur
    cursor = nutrient_analyses.find(
        {"user_id": user_id}
    ).sort("analyzed_at", -1).limit(limit)
    
    analyses = await cursor.to_list(length=limit)
    
    # Nettoyage des résultats
    for analysis in analyses:
        analysis.pop("_id", None)
    
    logger.info(f"🥗 Historique nutritionnel récupéré pour user {user_id}: {len(analyses)} analyses")
    
    return {
        "user_id": user_id,
        "total": len(analyses),
        "analyses": analyses
    }