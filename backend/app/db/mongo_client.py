from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Charger les variables d'environnement (.env)
# Chercher le .env à la racine du projet (3 niveaux au-dessus)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Récupération des infos de connexion
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Initialisation du client MongoDB 
client = AsyncIOMotorClient(MONGO_URI)

# Référencement de la base de données principale
db = client[MONGO_DB]

async def get_database():
    """
    Retourne la base MongoDB 'feel_good'
    (utilisée par les services FastAPI pour insérer ou lire des données)
    """
    return db

