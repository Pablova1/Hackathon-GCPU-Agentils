"""
Configuration centralisée de l'application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

# Charger les variables d'environnement depuis la racine du projet
env_path = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Créer le dossier uploads
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    
    # Google Cloud / Vertex AI
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Instance globale des settings
settings = Settings()