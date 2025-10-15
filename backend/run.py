"""
Point d'entrée pour lancer l'API.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,  # Mode développement
        log_level=settings.LOG_LEVEL.lower()
    )