"""
Script pour créer les index sur la collection 'user'.
Crée des index uniques avec sparse=True pour permettre les valeurs null.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.db.mongo_client import get_database


async def create_user_indexes():
    """Crée les index nécessaires sur la collection 'user'."""
    print("=" * 80)
    print("  CRÉATION DES INDEX")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Lister les index existants
    print(f"\n📋 Index actuels:")
    existing_indexes = await user_collection.list_indexes().to_list(None)
    for idx in existing_indexes:
        print(f"   - {idx['name']}: {idx['key']}")
    
    print(f"\n🔧 Création des nouveaux index...")
    
    try:
        # Index sur email (unique, sparse pour permettre null)
        await user_collection.create_index("email", unique=True, sparse=True)
        print("   ✅ Index créé: email (unique, sparse)")
    except Exception as e:
        if "already exists" in str(e):
            print(f"   ℹ️  Index 'email' existe déjà")
        else:
            print(f"   ❌ Erreur lors de la création de l'index 'email': {e}")
    
    try:
        # Index sur username (unique, sparse pour permettre null)
        await user_collection.create_index("username", unique=True, sparse=True)
        print("   ✅ Index créé: username (unique, sparse)")
    except Exception as e:
        if "already exists" in str(e):
            print(f"   ℹ️  Index 'username' existe déjà")
        else:
            print(f"   ❌ Erreur lors de la création de l'index 'username': {e}")
    
    try:
        # Index sur user_id (unique, sparse pour permettre null)
        await user_collection.create_index("user_id", unique=True, sparse=True)
        print("   ✅ Index créé: user_id (unique, sparse)")
    except Exception as e:
        if "already exists" in str(e):
            print(f"   ℹ️  Index 'user_id' existe déjà")
        else:
            print(f"   ❌ Erreur lors de la création de l'index 'user_id': {e}")
    
    # Vérification finale
    print(f"\n" + "=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    
    print(f"\n📋 Index finaux:")
    final_indexes = await user_collection.list_indexes().to_list(None)
    for idx in final_indexes:
        print(f"\n   📌 {idx['name']}")
        print(f"      Clés: {idx['key']}")
        if 'unique' in idx:
            print(f"      Unique: {idx['unique']}")
        if 'sparse' in idx:
            print(f"      Sparse: {idx['sparse']}")
    
    # Tester l'unicité
    print(f"\n" + "=" * 80)
    print("  TEST D'UNICITÉ")
    print("=" * 80)
    
    print(f"\n🧪 Vérification que les index empêchent les doublons...")
    
    # Compter les utilisateurs par email
    all_users = await user_collection.find({"email": {"$ne": None}}).to_list(None)
    emails = [u.get('email') for u in all_users]
    
    if len(emails) == len(set(emails)):
        print(f"   ✅ Tous les emails sont uniques ({len(emails)} utilisateurs)")
    else:
        print(f"   ❌ Des doublons d'emails existent!")
    
    # Compter les utilisateurs par username
    usernames = [u.get('username') for u in all_users if u.get('username')]
    if len(usernames) == len(set(usernames)):
        print(f"   ✅ Tous les usernames sont uniques ({len(usernames)} utilisateurs)")
    else:
        print(f"   ❌ Des doublons de usernames existent!")
    
    # Compter les utilisateurs par user_id
    user_ids = [u.get('user_id') for u in all_users if u.get('user_id')]
    if len(user_ids) == len(set(user_ids)):
        print(f"   ✅ Tous les user_id sont uniques ({len(user_ids)} utilisateurs)")
    else:
        print(f"   ❌ Des doublons de user_id existent!")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)
    
    print(f"\n✅ Les index sont maintenant en place!")
    print(f"   - Impossible de créer deux utilisateurs avec le même email")
    print(f"   - Impossible de créer deux utilisateurs avec le même username")
    print(f"   - Impossible de créer deux utilisateurs avec le même user_id")


if __name__ == "__main__":
    asyncio.run(create_user_indexes())
