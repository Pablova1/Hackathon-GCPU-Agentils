from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Charger les variables d'environnement (.env)
load_dotenv()

# Récupération des infos de connexion
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Initialisation du client MongoDB 
client = AsyncIOMotorClient(MONGO_URI)

# On référence la base de données principale
db = client[MONGO_DB]
