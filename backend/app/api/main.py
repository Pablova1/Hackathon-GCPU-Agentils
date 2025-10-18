"""
Point d'entrée principal de l'API FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.api.routes import api_router
from app.api.onboarding import router as onboarding_router
from app.api.profile_router import router as profile_router
from app.api.meal_router import router as meal_router

# Configuration du logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API pour analyser la composition d'assiettes à partir d'images",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(api_router, prefix="/api")
app.include_router(onboarding_router)  # Sans préfixe /api
app.include_router(profile_router)     # Sans préfixe /api
app.include_router(meal_router)        # Sans préfixe /api


# Routes principales
@app.get("/")
async def root():
    """Page d'accueil de l'API."""
    return {
        "message": f"Bienvenue sur {settings.API_TITLE}",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/api/analyze/health",
        "endpoints": {
            "analyze_plate": "POST /api/analyze/plate",
            "analyze_nutrients": "POST /api/analyze/nutrients"
        }
    }


@app.get("/health")
async def global_health():
    """Health check global de l'API."""
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION
    }


# Gestion globale des erreurs
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "Une erreur interne est survenue",
            "error": str(exc)
        }
    )


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Événement au démarrage de l'API."""
    logger.info(f"🚀 Démarrage de {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"📁 Dossier uploads: {settings.UPLOAD_DIR}")


@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt de l'API."""
    logger.info("🛑 Arrêt de l'API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)