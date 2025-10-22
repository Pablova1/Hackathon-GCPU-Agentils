"""
Script de migration: users (pluriel) → user (singulier)
Migre les documents de la collection 'users' vers 'user' et supprime l'ancienne collection.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.db.mongo_client import get_database


async def migrate_users_collection():
    """Migre la collection 'users' vers 'user'."""
    print("=" * 60)
    print("  MIGRATION: users → user")
    print("=" * 60)
    
    db = await get_database()
    
    # Vérifier si 'users' existe
    collections = await db.list_collection_names()
    
    if "users" not in collections:
        print("✅ Collection 'users' n'existe pas. Rien à migrer.")
        return
    
    users_plural = db["users"]  # Ancienne collection (pluriel)
    user_singular = db["user"]  # Nouvelle collection (singulier)
    
    # Compter les documents
    count_plural = await users_plural.count_documents({})
    count_singular = await user_singular.count_documents({})
    
    print(f"\n📊 État actuel:")
    print(f"   - 'users' (pluriel): {count_plural} documents")
    print(f"   - 'user' (singulier): {count_singular} documents")
    
    if count_plural == 0:
        print("\n✅ Collection 'users' est vide. On peut la supprimer.")
        await users_plural.drop()
        print("✅ Collection 'users' supprimée!")
        return
    
    # Afficher les documents à migrer
    print(f"\n📄 Documents à migrer:")
    async for doc in users_plural.find():
        print(f"   - {doc.get('username', 'N/A')} ({doc.get('email', 'N/A')})")
    
    # Demander confirmation
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Copier {count_plural} document(s) de 'users' vers 'user'")
    print(f"   2. Supprimer la collection 'users'")
    
    response = input("\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Migration annulée.")
        return
    
    # Migrer les documents
    print(f"\n🔄 Migration en cours...")
    migrated_count = 0
    
    async for doc in users_plural.find():
        # Vérifier si l'utilisateur existe déjà dans 'user'
        user_id = doc.get("user_id")
        email = doc.get("email")
        username = doc.get("username")
        
        existing = None
        if user_id:
            existing = await user_singular.find_one({"user_id": user_id})
        elif email:
            existing = await user_singular.find_one({"email": email})
        elif username:
            existing = await user_singular.find_one({"username": username})
        
        if existing:
            print(f"   ⚠️  Utilisateur déjà existant: {username or email or user_id}")
            print(f"      → Fusion des données...")
            
            # Fusionner les données (priorité aux données de 'users')
            update_data = {}
            
            # Champs d'authentification (priorité à 'users')
            if doc.get("user_id"):
                update_data["user_id"] = doc["user_id"]
            if doc.get("email"):
                update_data["email"] = doc["email"]
            if doc.get("username"):
                update_data["username"] = doc["username"]
            if doc.get("password_hash"):
                update_data["password_hash"] = doc["password_hash"]
            if doc.get("created_at"):
                update_data["created_at"] = doc["created_at"]
            
            # Mettre à jour
            await user_singular.update_one(
                {"_id": existing["_id"]},
                {"$set": update_data}
            )
            print(f"      ✅ Fusionné avec succès")
        else:
            # Insérer le nouveau document
            await user_singular.insert_one(doc)
            print(f"   ✅ Migré: {username or email or user_id}")
        
        migrated_count += 1
    
    print(f"\n✅ {migrated_count} document(s) migré(s)")
    
    # Supprimer l'ancienne collection
    print(f"\n🗑️  Suppression de la collection 'users'...")
    await users_plural.drop()
    print("✅ Collection 'users' supprimée!")
    
    # Vérification finale
    count_final = await user_singular.count_documents({})
    print(f"\n📊 État final:")
    print(f"   - 'user' (singulier): {count_final} documents")
    
    print("\n" + "=" * 60)
    print("  MIGRATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate_users_collection())
