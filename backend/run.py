"""
Point d'entrée pour lancer l'API.
"""

import uvicorn
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print(" Démarrage de Food Analyzer API")
    print(" http://localhost:8000")
    print(" Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "app.api.main:app",  # Le chemin est correct
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )