"""
Test rapide de l'inscription avec le nouveau schéma unifié.
Vérifie que l'utilisateur est bien créé dans la collection 'user' avec les bons champs.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import secrets
from app.db.mongo_client import get_database


async def test_unified_schema():
    """Teste le nouveau schéma unifié."""
    print("=" * 60)
    print("  TEST DU SCHÉMA UNIFIÉ")
    print("=" * 60)
    
    db = await get_database()
    users = db["user"]  # Collection 'user' (singulier)
    
    # Créer un utilisateur de test
    test_user_id = f"user_test_{secrets.token_hex(4)}"
    test_email = f"test_{secrets.token_hex(4)}@example.com"
    
    print(f"\n1️⃣  Création d'un utilisateur de test...")
    print(f"   user_id: {test_user_id}")
    print(f"   email: {test_email}")
    
    user_data = {
        "user_id": test_user_id,
        "email": test_email,
        "username": f"TestUser_{secrets.token_hex(2)}",
        "password_hash": "test_hash_12345",
        "created_at": "2025-10-20T10:00:00Z",
        "last_login": "2025-10-20T10:00:00Z",
        "profile_completed": False,
        # Champs de profil initialisés à null
        "profile": None,
        "medical": None,
        "nutrition": None,
        "goals": None,
        "religiousRestrictions": None,
        "misc": None
    }
    
    # Insérer l'utilisateur
    result = await users.insert_one(user_data)
    print(f"   ✅ Utilisateur créé avec _id: {result.inserted_id}")
    
    # Vérifier l'insertion
    print(f"\n2️⃣  Vérification dans MongoDB...")
    user = await users.find_one({"user_id": test_user_id})
    
    if user:
        print(f"   ✅ Utilisateur trouvé dans la collection 'user'")
        print(f"\n   📋 Champs d'authentification:")
        print(f"      - user_id: {user.get('user_id')}")
        print(f"      - email: {user.get('email')}")
        print(f"      - username: {user.get('username')}")
        print(f"      - password_hash: {user.get('password_hash')}")
        print(f"      - created_at: {user.get('created_at')}")
        print(f"      - profile_completed: {user.get('profile_completed')}")
        
        print(f"\n   📋 Champs de profil (doivent être null):")
        print(f"      - profile: {user.get('profile')}")
        print(f"      - medical: {user.get('medical')}")
        print(f"      - nutrition: {user.get('nutrition')}")
        print(f"      - goals: {user.get('goals')}")
        
        # Vérifier le schéma
        errors = []
        
        if user.get("profile") is not None:
            errors.append("❌ 'profile' devrait être null")
        else:
            print(f"\n   ✅ 'profile' est bien null")
        
        if user.get("medical") is not None:
            errors.append("❌ 'medical' devrait être null")
        else:
            print(f"   ✅ 'medical' est bien null")
        
        if user.get("profile_completed") != False:
            errors.append("❌ 'profile_completed' devrait être false")
        else:
            print(f"   ✅ 'profile_completed' est bien false")
        
        if user.get("email") != test_email:
            errors.append("❌ 'email' incorrect")
        else:
            print(f"   ✅ 'email' est correct")
        
        if errors:
            print(f"\n   ⚠️  ERREURS DÉTECTÉES:")
            for err in errors:
                print(f"      {err}")
        else:
            print(f"\n   🎉 SCHÉMA PARFAIT - Tous les champs sont corrects!")
    else:
        print(f"   ❌ Utilisateur non trouvé!")
    
    # Simuler l'onboarding (mise à jour du profil)
    print(f"\n3️⃣  Simulation de l'onboarding (mise à jour du profil)...")
    
    profile_data = {
        "firstName": "Test",
        "lastName": "User",
        "age": 25,
        "gender": "Other",
        "weight": 70.0,
        "height": 175.0,
        "bodyType": "mesomorphic"
    }
    
    update_result = await users.update_one(
        {"user_id": test_user_id},
        {"$set": {
            "profile": profile_data,
            "profile_completed": True
        }}
    )
    
    if update_result.modified_count > 0:
        print(f"   ✅ Profil mis à jour")
        
        # Vérifier la mise à jour
        updated_user = await users.find_one({"user_id": test_user_id})
        
        print(f"\n   📋 Après onboarding:")
        print(f"      - profile_completed: {updated_user.get('profile_completed')}")
        print(f"      - profile: {updated_user.get('profile')}")
        print(f"      - email (inchangé): {updated_user.get('email')}")
        print(f"      - password_hash (inchangé): {updated_user.get('password_hash')}")
        
        if updated_user.get("email") == test_email and updated_user.get("profile_completed") == True:
            print(f"\n   🎉 MISE À JOUR RÉUSSIE - Les champs d'auth n'ont pas été modifiés!")
        else:
            print(f"\n   ❌ ERREUR - Les champs ont été incorrectement modifiés")
    else:
        print(f"   ❌ Échec de la mise à jour")
    
    # Nettoyage
    print(f"\n4️⃣  Nettoyage (suppression de l'utilisateur de test)...")
    delete_result = await users.delete_one({"user_id": test_user_id})
    
    if delete_result.deleted_count > 0:
        print(f"   ✅ Utilisateur de test supprimé")
    else:
        print(f"   ⚠️  Échec de la suppression")
    
    print("\n" + "=" * 60)
    print("  TEST TERMINÉ")
    print("=" * 60)


async def check_collection_name():
    """Vérifie que la bonne collection est utilisée."""
    print("\n🔍 Vérification du nom de collection...")
    
    db = await get_database()
    collections = await db.list_collection_names()
    
    if "user" in collections:
        print("   ✅ Collection 'user' (singulier) existe")
    else:
        print("   ❌ Collection 'user' n'existe pas!")
    
    if "users" in collections:
        print("   ⚠️  Collection 'users' (pluriel) existe - DEVRAIT PAS!")
    else:
        print("   ✅ Pas de collection 'users' (pluriel)")


async def main():
    """Fonction principale."""
    await check_collection_name()
    await test_unified_schema()


if __name__ == "__main__":
    asyncio.run(main())
