"""
Script de diagnostic pour vérifier l'état des suggestions dans la base de données.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def check_user_suggestions():
    """Vérifie l'état des suggestions pour tous les utilisateurs."""
    
    # Connexion à MongoDB (utiliser les mêmes credentials que l'app)
    import os
    from pathlib import Path
    from dotenv import load_dotenv
    
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
    users_collection = db["user"]
    
    # Récupérer tous les utilisateurs (filtrer seulement ceux avec email)
    users_cursor = users_collection.find({"email": {"$exists": True, "$ne": None, "$ne": ""}})
    users = await users_cursor.to_list(length=None)
    
    print(f"\n📊 Analyse de {len(users)} utilisateur(s) avec email\n")
    print("=" * 80)
    
    for user in users:
        user_id = user.get("user_id", "N/A")
        email = user.get("email", "N/A")
        
        print(f"\n👤 Utilisateur: {user_id}")
        print(f"   Email: {email}")
        
        # Vérifier si l'utilisateur a un profil complet
        profile = user.get("profile", {})
        if profile is None:
            profile = {}
        medical = user.get("medical", {})
        if medical is None:
            medical = {}
        nutrition = user.get("nutrition", {})
        if nutrition is None:
            nutrition = {}
        goals = user.get("goals", {})
        if goals is None:
            goals = {}
        misc = user.get("misc", {})
        if misc is None:
            misc = {}
        
        print(f"\n   📋 Profil:")
        print(f"      Age: {profile.get('age', 'N/A')}")
        print(f"      Poids: {profile.get('weight', 'N/A')} kg")
        print(f"      Taille: {profile.get('height', 'N/A')} cm")
        print(f"      Sexe: {profile.get('gender', 'N/A')}")
        print(f"      Morphologie: {profile.get('bodyType', 'N/A')}")
        
        print(f"\n   🎯 Objectifs:")
        print(f"      Prise de muscle: {goals.get('muscle_gain', False)}")
        print(f"      Perte de poids: {goals.get('weight_loss', False)}")
        print(f"      Performance: {goals.get('performance', False)}")
        print(f"      Maintien forme: {goals.get('maintain_shape', False)}")
        
        print(f"\n   🏃 Activité:")
        print(f"      Niveau: {misc.get('activityLevel', 'N/A')}")
        print(f"      Sports: {misc.get('sports', [])}")
        
        print(f"\n   🍽️ Nutrition:")
        print(f"      Régime: {nutrition.get('diet', 'N/A')}")
        print(f"      Intolérances: {nutrition.get('intolerances', [])}")
        print(f"      Préférences: {nutrition.get('preferences', [])}")
        
        print(f"\n   💊 Médical:")
        print(f"      Allergies: {medical.get('allergies', [])}")
        print(f"      Traitements: {medical.get('treatments', [])}")
        
        # Vérifier last_suggestion
        last_suggestion = user.get("last_suggestion")
        
        print(f"\n   💡 Dernière suggestion:")
        if last_suggestion:
            status = last_suggestion.get("status", "N/A")
            generated_at = last_suggestion.get("generated_at", "N/A")
            
            print(f"      Statut: {status}")
            print(f"      Générée le: {generated_at}")
            
            if status == "failed":
                error = last_suggestion.get("error", "N/A")
                print(f"      ❌ Erreur: {error}")
            elif status == "completed":
                motivation = last_suggestion.get("motivation_message", "N/A")
                meals = last_suggestion.get("meal_suggestions", [])
                print(f"      ✅ Message motivation: {motivation[:100]}...")
                print(f"      ✅ Nombre de suggestions repas: {len(meals)}")
        else:
            print(f"      ⚠️ Aucune suggestion générée")
        
        print("\n" + "=" * 80)
    
    client.close()
    print("\n✅ Analyse terminée\n")

if __name__ == "__main__":
    asyncio.run(check_user_suggestions())
