"""
Configuration centralisée de l'application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

# Charger les variables d'environnement depuis la racine du projet
env_path = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Créer le dossier uploads
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Configuration cache
MAX_MESSAGES_PER_USER = 20

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")


class Settings:
    """Configuration de l'application."""
    
    # API
    API_TITLE: str = "Food Analyzer API"
    API_VERSION: str = "1.0.0"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # En prod: spécifier les domaines autorisés
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    UPLOAD_DIR: Path = UPLOAD_DIR
    
    # Google API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Instance globale des settings
settings = Settings()