"""
Test rapide pour vérifier que les utilisateurs sont créés dans 'user'
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le dossier backend au path pour permettre les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.user_store import create_user_document
from app.db.mongo_client import get_database
from datetime import datetime

async def test_user_creation():
    """Teste la création d'un utilisateur dans la collection 'user'."""
    
    # Données de test
    test_slots = {
        "firstName": "TestPrenom",
        "lastName": "TestNom",
        "age": 30,
        "gender": "Male",
        "weight": 75.0,
        "height": 180.0,
        "bodyType": "mesomorphic",  # Valeur valide: ectomorphic, mesomorphic, endomorphic, unknown
        "diet": "omnivore",
        "activityLevel": "moderate",
        "treatments": [],
        "allergies": [],
        "medicalHistory_personal": [],
        "medicalHistory_family": [],
        "birthControl_uses": False,
        "intolerances": [],
        "preferences_liked": [],
        "preferences_disliked": [],
        "preferences_general": [],
        "muscleGain": False,
        "weightLoss": False,
        "performance": False,
        "maintainShape": True,
        "sports": [],
        "occupation": None,
        "notes": None,
    }
    
    user_id = f"test_singulier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n🧪 Création d'un utilisateur de test...")
    print(f"   User ID: {user_id}")
    
    # Créer l'utilisateur
    user_doc = await create_user_document(user_id, test_slots)
    
    print(f"✅ Utilisateur créé avec l'ID: {user_doc.get('_id')}")
    
    # Vérifier dans quelle collection il est
    db = await get_database()
    
    # Vérifier dans 'user'
    user_collection = db["user"]
    user_in_user = await user_collection.find_one({"user_id": user_id})
    
    # Vérifier dans 'users' (ne devrait pas y être)
    users_collection = db["users"]
    user_in_users = await users_collection.find_one({"user_id": user_id})
    
    print(f"\n📊 Vérification:")
    print(f"   Dans collection 'user': {'✅ OUI' if user_in_user else '❌ NON'}")
    print(f"   Dans collection 'users': {'⚠️ OUI (devrait pas!)' if user_in_users else '✅ NON'}")
    
    if user_in_user and not user_in_users:
        print(f"\n🎉 SUCCÈS! L'utilisateur est bien dans la collection 'user' (singulier)")
    else:
        print(f"\n❌ ERREUR! L'utilisateur n'est pas au bon endroit")
    
    # Afficher les compteurs
    count_user = await user_collection.count_documents({})
    count_users = await users_collection.count_documents({})
    print(f"\n📈 Nombre total de documents:")
    print(f"   Collection 'user': {count_user}")
    print(f"   Collection 'users': {count_users}")

if __name__ == "__main__":
    asyncio.run(test_user_creation())
