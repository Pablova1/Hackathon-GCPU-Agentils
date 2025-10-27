"""
Script pour vérifier les repas d'un utilisateur.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

async def check_user_meals():
    """Vérifie les repas d'un utilisateur."""
    
    # Charger .env
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB")
    
    client = AsyncIOMotorClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000
    )
    db = client[MONGO_DB]
    meals_collection = db["meals"]
    
    user_id = "user_c425c778ac661067"
    
    # Récupérer tous les repas de l'utilisateur
    meals_cursor = meals_collection.find({"userId": user_id}).sort("dateScanned", -1)
    meals = await meals_cursor.to_list(length=None)
    
    print(f"\n🍽️ Repas de l'utilisateur {user_id}\n")
    print("=" * 80)
    print(f"\nNombre total de repas: {len(meals)}\n")
    
    for i, meal in enumerate(meals, 1):
        print(f"\n{i}. {meal.get('name', 'Sans nom')}")
        print(f"   Date: {meal.get('dateScanned', 'N/A')}")
        print(f"   Ingrédients: {meal.get('ingredients', [])}")
        
        nutrients = meal.get('nutrients', {})
        print(f"   Nutriments:")
        print(f"      Calories: {nutrients.get('energy_kcal', nutrients.get('calories', 0))} kcal")
        print(f"      Protéines: {nutrients.get('proteins_g', nutrients.get('protein', 0))} g")
        print(f"      Glucides: {nutrients.get('carbohydrates_g', nutrients.get('carbohydrates', 0))} g")
        print(f"      Lipides: {nutrients.get('lipids_g', nutrients.get('fat', 0))} g")
    
    print("\n" + "=" * 80)
    client.close()

if __name__ == "__main__":
    asyncio.run(check_user_meals())
