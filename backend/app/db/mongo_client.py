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

# Variables globales pour le client (lazy initialization)
client = None
db = None

def get_mongo_client():
    """
    Retourne le client MongoDB (lazy initialization)
    """
    global client, db
    if client is None:
        # Validation minimale des variables d'environnement
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable is not set or empty")
        if not MONGO_DB:
            raise ValueError("MONGO_DB environment variable is not set or empty")

        # Nettoyer la chaîne et vérifier la forme simple
        uri = MONGO_URI.strip()
        if uri == "" or "mongodb" not in uri:
            raise ValueError(f"MONGO_URI looks invalid: '{uri}'")

        # Initialisation du client MongoDB asynchrone (Motor) avec configuration SSL
        try:
            client = AsyncIOMotorClient(
                uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            # Référencement de la base de données principale
            db = client[MONGO_DB]
        except Exception as e:
            # Remonter une erreur explicite utile pour le debug (logs/container)
            raise ValueError(f"Failed to initialize Mongo client with MONGO_URI: {e}") from e
    return client, db

async def get_database():
    """
    Retourne la base MongoDB 'feel_good' (async)
    (utilisée par les services FastAPI et les agents)
    """
    _, database = get_mongo_client()
    return database
    return db

