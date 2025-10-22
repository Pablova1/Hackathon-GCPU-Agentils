"""
Script pour rendre les usernames uniques.
Ajoute un suffixe numérique aux usernames dupliqués.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from collections import defaultdict
from app.db.mongo_client import get_database


async def make_usernames_unique():
    """Rend tous les usernames uniques en ajoutant un suffixe."""
    print("=" * 80)
    print("  UNIFORMISATION DES USERNAMES")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Trouver les usernames dupliqués
    all_users = await user_collection.find({"username": {"$ne": None}}).to_list(None)
    
    username_counts = defaultdict(list)
    for user in all_users:
        username = user.get('username')
        if username:
            username_counts[username].append(user)
    
    # Identifier les doublons
    duplicates = {username: users for username, users in username_counts.items() if len(users) > 1}
    
    print(f"\n📊 Analyse des usernames:")
    print(f"   - Total d'utilisateurs: {len(all_users)}")
    print(f"   - Usernames uniques: {len(username_counts)}")
    print(f"   - Usernames dupliqués: {len(duplicates)}")
    
    if not duplicates:
        print("\n✅ Tous les usernames sont déjà uniques!")
        return
    
    # Afficher les doublons
    print(f"\n📋 Usernames dupliqués:")
    for username, users in duplicates.items():
        print(f"\n   👤 {username} ({len(users)} utilisateurs)")
        for user in users:
            email = user.get('email', 'N/A')
            user_id = user.get('user_id', 'N/A')
            print(f"      - {email:45} (user_id: {user_id})")
    
    # Demander confirmation
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Garder le premier utilisateur avec son username original")
    print(f"   2. Ajouter un suffixe _2, _3, etc. aux autres")
    print(f"   Exemple: sophie_durand")
    print(f"            → sophie_durand (1er)")
    print(f"            → sophie_durand_2 (2ème)")
    
    response = input("\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    # Traiter les doublons
    print(f"\n🔄 Uniformisation en cours...\n")
    updated_count = 0
    
    for username, users in duplicates.items():
        # Garder le premier, modifier les autres
        for idx, user in enumerate(users[1:], start=2):
            new_username = f"{username}_{idx}"
            
            # Mettre à jour
            result = await user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"username": new_username}}
            )
            
            if result.modified_count > 0:
                email = user.get('email', 'N/A')
                print(f"   ✅ {email:45} | {username:20} → {new_username}")
                updated_count += 1
            else:
                print(f"   ⚠️  Échec de la mise à jour pour {user.get('email', 'N/A')}")
    
    print(f"\n✅ {updated_count} usernames mis à jour")
    
    # Vérification finale
    print(f"\n" + "=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    
    all_users_updated = await user_collection.find({"username": {"$ne": None}}).to_list(None)
    
    username_set = set()
    duplicates_found = False
    
    print(f"\n📋 Liste complète des utilisateurs:")
    for idx, user in enumerate(all_users_updated, 1):
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        
        # Vérifier si doublon
        if username in username_set:
            print(f"   ❌ {idx:2d}. {username:25} | {email:45} | ⚠️  DOUBLON!")
            duplicates_found = True
        else:
            print(f"   ✅ {idx:2d}. {username:25} | {email}")
            username_set.add(username)
    
    if not duplicates_found:
        print(f"\n✅ Tous les usernames sont maintenant uniques!")
    else:
        print(f"\n⚠️  Des doublons persistent!")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(make_usernames_unique())
