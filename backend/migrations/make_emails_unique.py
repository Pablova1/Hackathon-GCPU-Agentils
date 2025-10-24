"""
Script pour rendre les emails uniques.
Ajoute un suffixe numérique aux emails dupliqués.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from collections import defaultdict
from app.db.mongo_client import get_database


async def make_emails_unique():
    """Rend tous les emails uniques en ajoutant un suffixe."""
    print("=" * 80)
    print("  UNIFORMISATION DES EMAILS")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Trouver les emails dupliqués
    all_users = await user_collection.find({"email": {"$ne": None}}).to_list(None)
    
    email_counts = defaultdict(list)
    for user in all_users:
        email = user.get('email')
        if email:
            email_counts[email].append(user)
    
    # Identifier les doublons
    duplicates = {email: users for email, users in email_counts.items() if len(users) > 1}
    
    print(f"\n📊 Analyse des emails:")
    print(f"   - Total d'utilisateurs avec email: {len(all_users)}")
    print(f"   - Emails uniques: {len(email_counts)}")
    print(f"   - Emails dupliqués: {len(duplicates)}")
    
    if not duplicates:
        print("\n✅ Tous les emails sont déjà uniques!")
        return
    
    # Afficher les doublons
    print(f"\n📋 Emails dupliqués:")
    for email, users in duplicates.items():
        print(f"\n   📧 {email} ({len(users)} utilisateurs)")
        for user in users:
            username = user.get('username', 'N/A')
            user_id = user.get('user_id', 'N/A')
            print(f"      - {username:25} (user_id: {user_id})")
    
    # Demander confirmation
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Garder le premier utilisateur avec son email original")
    print(f"   2. Ajouter un suffixe _2, _3, etc. aux autres")
    print(f"   Exemple: sophie.martin@test-hackathon.com")
    print(f"            → sophie.martin@test-hackathon.com (1er)")
    print(f"            → sophie.martin_2@test-hackathon.com (2ème)")
    print(f"            → sophie.martin_3@test-hackathon.com (3ème)")
    
    response = input("\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    # Traiter les doublons
    print(f"\n🔄 Uniformisation en cours...\n")
    updated_count = 0
    
    for email, users in duplicates.items():
        # Garder le premier, modifier les autres
        for idx, user in enumerate(users[1:], start=2):
            # Extraire le nom et le domaine
            if '@' in email:
                local, domain = email.rsplit('@', 1)
                new_email = f"{local}_{idx}@{domain}"
            else:
                new_email = f"{email}_{idx}"
            
            # Mettre à jour
            result = await user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"email": new_email}}
            )
            
            if result.modified_count > 0:
                username = user.get('username', 'N/A')
                print(f"   ✅ {username:25} | {email:45} → {new_email}")
                updated_count += 1
            else:
                print(f"   ⚠️  Échec de la mise à jour pour {user.get('username', 'N/A')}")
    
    print(f"\n✅ {updated_count} emails mis à jour")
    
    # Vérification finale
    print(f"\n" + "=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    
    all_users_updated = await user_collection.find({"email": {"$ne": None}}).to_list(None)
    
    email_set = set()
    duplicates_found = False
    
    print(f"\n📋 Liste complète des utilisateurs:")
    for idx, user in enumerate(all_users_updated, 1):
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        
        # Vérifier si doublon
        if email in email_set:
            print(f"   ❌ {idx:2d}. {username:25} | {email:45} | ⚠️  DOUBLON!")
            duplicates_found = True
        else:
            print(f"   ✅ {idx:2d}. {username:25} | {email}")
            email_set.add(email)
    
    if not duplicates_found:
        print(f"\n✅ Tous les emails sont maintenant uniques!")
    else:
        print(f"\n⚠️  Des doublons persistent, vérifiez la base de données")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(make_emails_unique())
