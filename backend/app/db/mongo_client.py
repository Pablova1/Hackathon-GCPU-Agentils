from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Charger les variables d'environnement (.env)
# From backend/app/db/mongo_client.py -> backend/.env (4 niveaux au-dessus)
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Récupération des infos de connexion
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Initialisation du client MongoDB asynchrone (Motor) avec configuration SSL
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000
)

# Référencement de la base de données principale
db = client[MONGO_DB]

async def get_database():
    """
    Retourne la base MongoDB 'feel_good' (async)
    (utilisée par les services FastAPI et les agents)
    """
    return db

