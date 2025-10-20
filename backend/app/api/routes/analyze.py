"""
Routes pour l'analyse d'assiettes.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import shutil
from pathlib import Path
import logging
import uuid
from datetime import datetime

from fastapi.encoders import jsonable_encoder

from app.core.config import settings
# Modifie cette ligne pour importer les deux fonctions
from app.ai.agents.agent_initializer import get_food_analyzer, get_nutrient_analyzer
from app.middleware.session_manager import get_current_session, get_optional_session, SessionManager
from app.db.mongo_client import get_database

logger = logging.getLogger(__name__)

# Création du router
router = APIRouter()


# Modèles Pydantic
class Aliment(BaseModel):
    name: str
    estimated_quantity: int

class AnalyseResponse(BaseModel):
    success: bool
    aliments: List[Aliment]
    nombre_aliments: int
    message: str = ""


@router.post("/plate", response_model=AnalyseResponse)
async def analyze_plate(
    file: UploadFile = File(...),
    session: dict = Depends(get_current_session)
):
    """
    Analyse une image d'assiette et retourne les aliments détectés.
    
    **Authentification requise** : Vous devez fournir un header `X-Session-Token`.
    
    - **file**: Image de l'assiette (JPG, PNG, JPEG, WEBP)
    
    Headers:
        - X-Session-Token: Token de session valide
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
    
    # Récupération de l'agent
    analyzer = get_food_analyzer()
    
    # Génération d'un nom de fichier unique
    import uuid
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = settings.UPLOAD_DIR / unique_filename
    
    try:
        # Sauvegarde du fichier uploadé
        with temp_file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Image sauvegardée: {temp_file_path} pour user {user_id}")
        
        # Analyse de l'image
        result = analyzer.analyze_plate(str(temp_file_path))
        
        # Formatage de la réponse
        aliments = result.get("foods", [])
        
        # Convertir estimated_quantity en entier pour chaque aliment
        for aliment in aliments:
            aliment["estimated_quantity"] = int(aliment["estimated_quantity"])

        # 🆕 SAUVEGARDE de l'analyse dans MongoDB
        db = await get_database()
        analyses_collection = db["plate_analyses"]
        
        analysis_record = {
            "user_id": user_id,
            "session_token": session_token,
            "image_filename": unique_filename,
            "aliments": aliments,
            "nombre_aliments": len(aliments),
            "analyzed_at": datetime.now().isoformat()
        }
        
        await analyses_collection.insert_one(analysis_record)
        
        # Mise à jour des statistiques de session
        await SessionManager.update_session_metadata(
            session_token,
            {"metadata.total_analyses": 1}
        )
        
        response = {
            "success": True,
            "aliments": aliments,
            "nombre_aliments": len(aliments),
            "message": f"{len(aliments)} aliment(s) détecté(s)"
        }
        
        logger.info(f"✅ Analyse réussie pour user {user_id}: {response['nombre_aliments']} aliments")
        
        return response
    
    except ValueError as e:
        # Erreur de parsing JSON
        logger.error(f"Erreur de parsing: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Erreur lors de l'analyse de l'image: {str(e)}"
        )
    
    except Exception as e:
        # Autres erreurs
        logger.error(f"Erreur lors de l'analyse: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne: {str(e)}"
        )
    
    finally:
        # Nettoyage du fichier temporaire
        if temp_file_path.exists():
            try:
                temp_file_path.unlink()
                logger.info(f"Fichier temporaire supprimé")
            except Exception as e:
                logger.warning(f"Impossible de supprimer {temp_file_path}: {e}")


@router.post("/nutrients")
async def analyze_nutrients(
    aliments: List[Aliment],
    session: dict = Depends(get_current_session)
):
    """
    Analyse les nutriments pour une liste d'aliments.
    
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

        # Conversion des aliments en dictionnaire
        aliments_data = [
            {"name": aliment.name, "estimated_quantity": aliment.estimated_quantity}
            for aliment in aliments
        ]

        # Log the structured aliments data
        logger.info(f"Structured aliments data: {aliments_data}")

        # Récupération de l'agent
        nutrient_analyzer = get_nutrient_analyzer()

        # Appel de l'analyse des nutriments
        result = nutrient_analyzer.analyze_nutrients(aliments_data)

        # Log the result from the nutrient analyzer
        logger.info(f"Nutrient analysis result: {result}")

        logger.info("=========On va faire la somme des nutriments=========")
        # Connect the API output to the nutrient summary function
        from app.services.nutrient_summary import calculate_nutrient_summary
        nutrient_summary = calculate_nutrient_summary(result)

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

        return {
            "success": True,
            "nutrients": result,
            "message": "Analyse des nutriments réussie."
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


@router.get("/health")
async def health_check():
    """Vérifie l'état des agents d'analyse."""
    try:
        food_analyzer = get_food_analyzer()
        nutrient_analyzer = get_nutrient_analyzer()
        
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
