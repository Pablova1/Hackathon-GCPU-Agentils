from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URI")
db_name = os.getenv("MONGO_DB")

client = MongoClient(uri)
db = client[db_name]
print("Connexion réussie à :", db.name)
print("Collections disponibles :", db.list_collection_names())
