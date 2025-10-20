"""
Script de remplissage des données d'authentification manquantes.
Remplit les champs email, username, password_hash pour les utilisateurs qui ont un profil mais pas d'auth.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import secrets
import hashlib
from datetime import datetime
from app.db.mongo_client import get_database


def generate_fake_auth_data(index: int, profile_data: dict):
    """Génère des données d'authentification factices basées sur le profil."""
    # Utiliser les données du profil si disponibles
    if profile_data:
        first_name = profile_data.get('firstName', f'User{index}')
        last_name = profile_data.get('lastName', f'Test{index}')
        profile_email = profile_data.get('email', '')
    else:
        first_name = f'User{index}'
        last_name = f'Test{index}'
        profile_email = ''
    
    # Générer un username basé sur le prénom/nom
    username = f"{first_name.lower()}_{last_name.lower()}"
    
    # Utiliser l'email du profil ou en générer un
    if profile_email and '@' in profile_email:
        email = profile_email
    else:
        email = f"{first_name.lower()}.{last_name.lower()}@test-hackathon.com"
    
    # Générer un user_id unique
    user_id = f"user_{secrets.token_hex(8)}"
    
    # Générer un hash de mot de passe (password: "Test123!")
    password = "Test123!"
    password_hash = hashlib.sha256((password + user_id).encode()).hexdigest()
    
    return {
        "user_id": user_id,
        "email": email,
        "username": username,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
        "profile_completed": True  # Ils ont déjà fait l'onboarding
    }


async def fill_missing_auth_data():
    """Remplit les données d'authentification manquantes."""
    print("=" * 80)
    print("  REMPLISSAGE DES DONNÉES D'AUTHENTIFICATION")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Trouver tous les utilisateurs sans email (non authentifiés)
    users_without_auth = await user_collection.find({
        "$or": [
            {"email": None},
            {"email": {"$exists": False}}
        ]
    }).to_list(None)
    
    print(f"\n📊 Utilisateurs sans authentification: {len(users_without_auth)}")
    
    if len(users_without_auth) == 0:
        print("\n✅ Tous les utilisateurs ont déjà des données d'authentification!")
        return
    
    # Afficher les utilisateurs à traiter
    print(f"\n📋 Liste des utilisateurs à compléter:")
    for idx, user in enumerate(users_without_auth, 1):
        profile = user.get('profile', {})
        first_name = profile.get('firstName', 'N/A')
        last_name = profile.get('lastName', 'N/A')
        print(f"   {idx}. {first_name} {last_name} (ID: {user['_id']})")
    
    # Demander confirmation
    print(f"\n⚠️  Cette opération va:")
    print(f"   1. Générer des données d'authentification pour {len(users_without_auth)} utilisateurs")
    print(f"   2. Mot de passe par défaut: 'Test123!' pour tous")
    print(f"   3. Email basé sur prénom.nom@test-hackathon.com")
    print(f"   4. Username basé sur prénom_nom")
    
    response = input("\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    # Traiter chaque utilisateur
    print(f"\n🔄 Remplissage en cours...\n")
    updated_count = 0
    
    for idx, user in enumerate(users_without_auth, 1):
        profile = user.get('profile', {})
        
        # Générer les données d'authentification
        auth_data = generate_fake_auth_data(idx, profile)
        
        # Mettre à jour le document
        result = await user_collection.update_one(
            {"_id": user["_id"]},
            {"$set": auth_data}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ {idx:2d}. {auth_data['username']:25} | {auth_data['email']:40} | {auth_data['user_id']}")
            updated_count += 1
        else:
            print(f"   ⚠️  {idx:2d}. Échec de la mise à jour")
    
    print(f"\n✅ {updated_count}/{len(users_without_auth)} utilisateurs mis à jour")
    
    # Afficher un résumé
    print(f"\n" + "=" * 80)
    print("  RÉSUMÉ DES COMPTES CRÉÉS")
    print("=" * 80)
    
    print(f"\n📋 Vous pouvez maintenant vous connecter avec:")
    print(f"   Mot de passe pour TOUS les comptes: Test123!")
    print(f"\n   Liste des comptes:")
    
    # Récupérer tous les utilisateurs avec auth
    all_users_with_auth = await user_collection.find({"email": {"$ne": None}}).to_list(None)
    
    for idx, user in enumerate(all_users_with_auth, 1):
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        has_profile = "✅ Profil complet" if user.get('profile') else "⚠️  Profil vide"
        print(f"   {idx:2d}. {username:25} | {email:40} | {has_profile}")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)
    
    # Vérification finale
    total_users = await user_collection.count_documents({})
    users_with_auth = await user_collection.count_documents({"email": {"$ne": None}})
    users_without_auth = total_users - users_with_auth
    
    print(f"\n📊 État final de la base de données:")
    print(f"   - Total d'utilisateurs: {total_users}")
    print(f"   - Avec authentification: {users_with_auth}")
    print(f"   - Sans authentification: {users_without_auth}")


if __name__ == "__main__":
    asyncio.run(fill_missing_auth_data())
