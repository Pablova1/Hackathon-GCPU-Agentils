"""
Script de vérification de la cohérence du schéma utilisateur.
Vérifie que toutes les références utilisent bien la collection 'user' (singulier).
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.db.mongo_client import get_database


async def check_database_consistency():
    """Vérifie la cohérence de la base de données."""
    print("🔍 Vérification de la cohérence de la base de données...\n")
    
    db = await get_database()
    
    # Lister toutes les collections
    collections = await db.list_collection_names()
    print(f"📋 Collections existantes: {', '.join(collections)}\n")
    
    # Vérifier la collection 'user'
    if "user" in collections:
        user_collection = db["user"]
        count = await user_collection.count_documents({})
        print(f"✅ Collection 'user' (singulier) existe: {count} documents")
        
        # Vérifier le schéma des documents
        sample = await user_collection.find_one({})
        if sample:
            print("\n📄 Structure d'un document exemple:")
            print(f"   - _id: {sample.get('_id')}")
            print(f"   - user_id: {sample.get('user_id')}")
            print(f"   - email: {sample.get('email')}")
            print(f"   - username: {sample.get('username')}")
            print(f"   - password_hash: {'✅' if sample.get('password_hash') else '❌'}")
            print(f"   - created_at: {sample.get('created_at')}")
            print(f"   - profile_completed: {sample.get('profile_completed')}")
            print(f"   - profile: {'✅ Présent' if sample.get('profile') else '❌ Null/Absent'}")
            print(f"   - medical: {'✅ Présent' if sample.get('medical') else '❌ Null/Absent'}")
            print(f"   - nutrition: {'✅ Présent' if sample.get('nutrition') else '❌ Null/Absent'}")
        
        # Compter les utilisateurs par statut
        completed = await user_collection.count_documents({"profile_completed": True})
        incomplete = await user_collection.count_documents({"profile_completed": False})
        print(f"\n📊 Statut des profils:")
        print(f"   - Profils complets (après onboarding): {completed}")
        print(f"   - Profils incomplets (auth seulement): {incomplete}")
    else:
        print("❌ Collection 'user' n'existe pas!")
    
    # Vérifier si 'users' (pluriel) existe
    if "users" in collections:
        users_collection = db["users"]
        count = await users_collection.count_documents({})
        print(f"\n⚠️  ATTENTION: Collection 'users' (pluriel) existe avec {count} documents")
        print(f"   → Cette collection ne devrait PAS exister!")
        print(f"   → Utiliser 'user' (singulier) uniquement")
    else:
        print("\n✅ Pas de collection 'users' (pluriel) - Correct!")
    
    # Vérifier les autres collections
    expected_collections = ["user", "user_sessions", "plate_analyses", "nutrient_analyses", "onboarding_sessions"]
    print(f"\n📋 Collections attendues:")
    for coll in expected_collections:
        if coll in collections:
            count = await db[coll].count_documents({})
            print(f"   ✅ {coll}: {count} documents")
        else:
            print(f"   ⚠️  {coll}: N'existe pas encore")
    
    # Vérifier les index
    print(f"\n🔑 Index sur la collection 'user':")
    if "user" in collections:
        indexes = await db["user"].list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"   - {idx['name']}: {idx['key']}")
    
    print("\n✅ Vérification terminée!")


async def create_indexes():
    """Crée les index nécessaires sur la collection 'user'."""
    print("\n🔧 Création des index...\n")
    
    db = await get_database()
    user_collection = db["user"]
    
    # Index sur email (unique)
    await user_collection.create_index("email", unique=True)
    print("   ✅ Index créé: email (unique)")
    
    # Index sur username (unique)
    await user_collection.create_index("username", unique=True)
    print("   ✅ Index créé: username (unique)")
    
    # Index sur user_id (unique)
    await user_collection.create_index("user_id", unique=True)
    print("   ✅ Index créé: user_id (unique)")
    
    print("\n✅ Index créés avec succès!")


async def show_sample_users():
    """Affiche quelques exemples d'utilisateurs."""
    print("\n👥 Exemples d'utilisateurs:\n")
    
    db = await get_database()
    user_collection = db["user"]
    
    # Utilisateurs sans profil
    incomplete = await user_collection.find({"profile_completed": False}).limit(3).to_list(length=3)
    if incomplete:
        print("📋 Utilisateurs sans profil (inscription seulement):")
        for user in incomplete:
            print(f"   - {user['username']} ({user['email']})")
            print(f"     user_id: {user['user_id']}")
            print(f"     created_at: {user.get('created_at')}")
    
    # Utilisateurs avec profil
    complete = await user_collection.find({"profile_completed": True}).limit(3).to_list(length=3)
    if complete:
        print("\n📋 Utilisateurs avec profil complet:")
        for user in complete:
            print(f"   - {user['username']} ({user['email']})")
            print(f"     user_id: {user['user_id']}")
            print(f"     profile: {user.get('profile', {}).get('firstName', 'N/A')} {user.get('profile', {}).get('lastName', 'N/A')}")
    
    if not incomplete and not complete:
        print("   ℹ️  Aucun utilisateur dans la base de données")


async def main():
    """Fonction principale."""
    print("=" * 60)
    print("  VÉRIFICATION DU SCHÉMA UTILISATEUR")
    print("=" * 60)
    
    await check_database_consistency()
    
    # Demander si on veut créer les index
    print("\n" + "=" * 60)
    response = input("\n🔧 Créer les index sur la collection 'user' ? (o/n): ")
    if response.lower() in ['o', 'y', 'oui', 'yes']:
        await create_indexes()
    
    # Afficher des exemples
    await show_sample_users()
    
    print("\n" + "=" * 60)
    print("  FIN DE LA VÉRIFICATION")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
