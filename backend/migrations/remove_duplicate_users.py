"""
Script pour supprimer les utilisateurs en doublon.
Garde le premier utilisateur de chaque groupe de doublons et supprime les autres.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from collections import defaultdict
from app.db.mongo_client import get_database


async def remove_duplicate_users():
    """Supprime les utilisateurs en doublon basés sur l'email."""
    print("=" * 80)
    print("  SUPPRESSION DES DOUBLONS")
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
    
    print(f"\n📊 Analyse:")
    print(f"   - Total d'utilisateurs: {len(all_users)}")
    print(f"   - Emails uniques: {len(email_counts)}")
    print(f"   - Emails dupliqués: {len(duplicates)}")
    
    if not duplicates:
        print("\n✅ Aucun doublon trouvé!")
        return
    
    # Calculer combien d'utilisateurs seront supprimés
    to_delete_count = sum(len(users) - 1 for users in duplicates.values())
    to_keep_count = len(duplicates)
    
    print(f"\n📋 Résumé:")
    print(f"   - Utilisateurs à garder: {to_keep_count}")
    print(f"   - Utilisateurs à supprimer: {to_delete_count}")
    
    # Afficher les détails
    print(f"\n📋 Détails des doublons:")
    for email, users in duplicates.items():
        print(f"\n   📧 {email}")
        print(f"      ✅ GARDER: {users[0].get('username', 'N/A'):25} (user_id: {users[0].get('user_id', 'N/A')}) - Créé: {users[0].get('created_at', 'N/A')}")
        for user in users[1:]:
            print(f"      ❌ SUPPRIMER: {user.get('username', 'N/A'):25} (user_id: {user.get('user_id', 'N/A')}) - Créé: {user.get('created_at', 'N/A')}")
    
    # Demander confirmation
    print(f"\n⚠️  ATTENTION: Cette opération est IRRÉVERSIBLE!")
    print(f"   {to_delete_count} utilisateur(s) seront DÉFINITIVEMENT supprimés")
    
    response = input("\n🔧 Êtes-vous SÛR de vouloir continuer ? (oui pour confirmer): ").strip().lower()
    
    if response != 'oui':
        print("❌ Opération annulée.")
        return
    
    # Supprimer les doublons
    print(f"\n🗑️  Suppression en cours...\n")
    deleted_count = 0
    
    for email, users in duplicates.items():
        # Garder le premier, supprimer les autres
        for user in users[1:]:
            result = await user_collection.delete_one({"_id": user["_id"]})
            
            if result.deleted_count > 0:
                username = user.get('username', 'N/A')
                user_id = user.get('user_id', 'N/A')
                print(f"   ✅ Supprimé: {username:25} | {email:45} | {user_id}")
                deleted_count += 1
            else:
                print(f"   ⚠️  Échec de la suppression pour {user.get('username', 'N/A')}")
    
    print(f"\n✅ {deleted_count}/{to_delete_count} utilisateurs supprimés")
    
    # Vérification finale
    print(f"\n" + "=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    
    all_users_final = await user_collection.find({"email": {"$ne": None}}).to_list(None)
    
    email_set = set()
    duplicates_found = False
    
    print(f"\n📊 État final:")
    print(f"   - Utilisateurs restants: {len(all_users_final)}")
    
    print(f"\n📋 Liste des utilisateurs:")
    for idx, user in enumerate(all_users_final, 1):
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        user_id = user.get('user_id', 'N/A')
        
        # Vérifier si doublon
        if email in email_set:
            print(f"   ❌ {idx:2d}. {username:25} | {email:45} | ⚠️  DOUBLON!")
            duplicates_found = True
        else:
            print(f"   ✅ {idx:2d}. {username:25} | {email:45} | {user_id}")
            email_set.add(email)
    
    if not duplicates_found:
        print(f"\n✅ Tous les emails sont maintenant uniques!")
    else:
        print(f"\n⚠️  Des doublons persistent!")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(remove_duplicate_users())
