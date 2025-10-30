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

# Initialisation du client MongoDB asynchrone (Motor)
# Détecter si on utilise MongoDB Atlas (URI contient "mongodb+srv")
is_atlas = MONGO_URI and "mongodb+srv" in MONGO_URI

client = AsyncIOMotorClient(
    MONGO_URI,
    tls=is_atlas,  # TLS activé automatiquement pour Atlas
    serverSelectionTimeoutMS=5000,  # Réduit de 10s à 5s
    connectTimeoutMS=5000,  # Réduit de 10s à 5s
    socketTimeoutMS=5000,  # Timeout pour les opérations socket
    maxPoolSize=10,  # Limite de connexions simultanées
    minPoolSize=1,  # Garde au moins 1 connexion ouverte
    maxIdleTimeMS=30000,  # Garde les connexions inactives 30s
    retryWrites=True,  # Retry automatique des écritures
    retryReads=True  # Retry automatique des lectures
)

# Référencement de la base de données principale
db = client[MONGO_DB]

async def get_database():
    """
    Retourne la base MongoDB 'feel_good' (async)
    (utilisée par les services FastAPI et les agents)
    """
    return db

