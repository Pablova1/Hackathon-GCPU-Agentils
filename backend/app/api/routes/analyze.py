"""
Routes pour l'analyse d'assiettes.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import shutil
from pathlib import Path
import logging

from app.core.config import settings
from app.ai.agents.agent_initializer import get_analyzer

logger = logging.getLogger(__name__)

# Création du router
router = APIRouter()


# Modèles Pydantic
class Aliment(BaseModel):
    nom: str
    quantite_estimee: str

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
    analyzer = get_analyzer()
    
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
        aliments = result.get("aliments", [])
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


@router.get("/health")
async def health_check():
    """Vérifie l'état de l'agent d'analyse."""
    try:
        analyzer = get_analyzer()
        return {
            "status": "healthy",
            "agent": "ready",
            "model": analyzer.model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service indisponible: {str(e)}"
        )