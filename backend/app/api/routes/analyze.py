"""
Routes pour l'analyse d'assiettes.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import shutil
from pathlib import Path
import logging
import uuid

from fastapi.encoders import jsonable_encoder

from app.core.config import settings
# Modifie cette ligne pour importer les deux fonctions
from app.ai.agents.agent_initializer import get_food_analyzer, get_nutrient_analyzer

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
async def analyze_plate(file: UploadFile = File(...)):
    """
    Analyse une image d'assiette et retourne les aliments détectés.
    
    - **file**: Image de l'assiette (JPG, PNG, JPEG, WEBP)
    """
    
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
        
        logger.info(f"Image sauvegardée: {temp_file_path}")
        
        # Analyse de l'image
        result = analyzer.analyze_plate(str(temp_file_path))
        
        # Formatage de la réponse
        aliments = result.get("foods", [])
        
        # Convertir estimated_quantity en entier pour chaque aliment
        for aliment in aliments:
            aliment["estimated_quantity"] = int(aliment["estimated_quantity"])

        response = {
            "success": True,
            "aliments": aliments,
            "nombre_aliments": len(aliments),
            "message": f"{len(aliments)} aliment(s) détecté(s)"
        }
        
        logger.info(f"Analyse réussie: {response['nombre_aliments']} aliments")
        
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
async def analyze_nutrients(aliments: List[Aliment]):
    """
    Analyse les nutriments pour une liste d'aliments.

    - **aliments**: Liste des aliments avec leur nom et quantité estimée.
    """
    try:
        # Log the raw aliments for debugging
        logger.info(f"Raw aliments received: {jsonable_encoder(aliments)}")

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