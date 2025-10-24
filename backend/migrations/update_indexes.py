"""
Script pour mettre à jour les index MongoDB après la réorganisation du schéma.
- Supprime l'index sur 'username' (n'existe plus)
- Supprime l'index sur 'email' (à la racine)
- Crée un index sur 'profile.email' (unique, sparse)
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.db.mongo_client import get_database


async def update_indexes():
    """Met à jour les index après la réorganisation du schéma."""
    print("=" * 80)
    print("  MISE À JOUR DES INDEX")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Lister les index existants
    print(f"\n📋 Index actuels:")
    existing_indexes = await user_collection.list_indexes().to_list(None)
    for idx in existing_indexes:
        print(f"   - {idx['name']}: {idx['key']}")
    
    # Demander confirmation
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Supprimer l'index sur 'username' (obsolète)")
    print(f"   2. Supprimer l'index sur 'email' (déplacé vers profile.email)")
    print(f"   3. Créer un index sur 'profile.email' (unique, sparse)")
    
    response = input(f"\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    print(f"\n🔄 Mise à jour en cours...\n")
    
    # Supprimer l'index 'username'
    try:
        await user_collection.drop_index("username_1")
        print("   ✅ Index 'username_1' supprimé")
    except Exception as e:
        if "index not found" in str(e).lower():
            print("   ℹ️  Index 'username_1' n'existe pas")
        else:
            print(f"   ⚠️  Erreur lors de la suppression de 'username_1': {e}")
    
    # Supprimer l'index 'email' à la racine
    try:
        await user_collection.drop_index("email_1")
        print("   ✅ Index 'email_1' supprimé")
    except Exception as e:
        if "index not found" in str(e).lower():
            print("   ℹ️  Index 'email_1' n'existe pas")
        else:
            print(f"   ⚠️  Erreur lors de la suppression de 'email_1': {e}")
    
    # Créer l'index sur 'profile.email'
    try:
        await user_collection.create_index("profile.email", unique=True, sparse=True)
        print("   ✅ Index 'profile.email' créé (unique, sparse)")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("   ℹ️  Index 'profile.email' existe déjà")
        else:
            print(f"   ❌ Erreur lors de la création de 'profile.email': {e}")
    
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
    
    print(f"\n🧪 Vérification des emails...")
    
    all_users = await user_collection.find({"profile.email": {"$ne": None}}).to_list(None)
    emails = [u.get('profile', {}).get('email') for u in all_users if u.get('profile', {}).get('email')]
    
    if len(emails) == len(set(emails)):
        print(f"   ✅ Tous les emails (profile.email) sont uniques ({len(emails)} utilisateurs)")
    else:
        print(f"   ❌ Des doublons d'emails existent!")
        
        # Afficher les doublons
        from collections import Counter
        duplicates = [email for email, count in Counter(emails).items() if count > 1]
        for dup in duplicates:
            print(f"      - {dup}")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)
    
    print(f"\n✅ Les index sont maintenant à jour!")
    print(f"   - L'email est stocké dans 'profile.email'")
    print(f"   - Le champ 'username' n'existe plus")
    print(f"   - Index de protection sur 'profile.email' (unique)")


if __name__ == "__main__":
    asyncio.run(update_indexes())
