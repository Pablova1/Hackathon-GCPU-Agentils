"""
Script de réorganisation du schéma utilisateur.
1. Déplace 'email' dans l'objet 'profile'
2. Supprime le champ 'username' (redondant avec firstName/lastName)
3. Réorganise les champs de 'profile' dans l'ordre logique
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from app.db.mongo_client import get_database


async def reorganize_user_schema():
    """Réorganise le schéma utilisateur."""
    print("=" * 80)
    print("  RÉORGANISATION DU SCHÉMA UTILISATEUR")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Compter les utilisateurs
    total_users = await user_collection.count_documents({})
    print(f"\n📊 Total d'utilisateurs: {total_users}")
    
    # Afficher le schéma actuel
    print(f"\n📋 Modifications à effectuer:")
    print(f"   1. Déplacer 'email' → 'profile.email'")
    print(f"   2. Supprimer 'username' (redondant)")
    print(f"   3. Réorganiser les champs de 'profile'")
    
    # Demander confirmation
    response = input(f"\n🔧 Continuer ? (o/n): ").strip().lower()
    
    if response != 'o':
        print("❌ Opération annulée.")
        return
    
    print(f"\n🔄 Migration en cours...\n")
    updated_count = 0
    
    async for user in user_collection.find():
        user_id = user.get('user_id', 'N/A')
        email = user.get('email')
        profile = user.get('profile', {})
        
        # Préparer les mises à jour
        update_operations = {}
        unset_operations = {}
        
        # 1. Déplacer email dans profile (si email existe et profile existe)
        if email and profile:
            # Ajouter email au profile
            profile['email'] = email
            update_operations['profile'] = profile
            # Marquer email racine pour suppression
            unset_operations['email'] = ""
            
        # 2. Supprimer username
        if 'username' in user:
            unset_operations['username'] = ""
        
        # Exécuter les mises à jour si nécessaire
        if update_operations or unset_operations:
            update_doc = {}
            if update_operations:
                update_doc['$set'] = update_operations
            if unset_operations:
                update_doc['$unset'] = unset_operations
            
            result = await user_collection.update_one(
                {"_id": user["_id"]},
                update_doc
            )
            
            if result.modified_count > 0:
                first_name = profile.get('firstName', 'N/A')
                last_name = profile.get('lastName', 'N/A')
                print(f"   ✅ {first_name} {last_name:20} | {email:45} | {user_id}")
                updated_count += 1
    
    print(f"\n✅ {updated_count}/{total_users} utilisateurs mis à jour")
    
    # Vérification finale
    print(f"\n" + "=" * 80)
    print("  VÉRIFICATION FINALE")
    print("=" * 80)
    
    print(f"\n📋 Structure des utilisateurs après migration:\n")
    
    async for user in user_collection.find().limit(2):
        first_name = user.get('profile', {}).get('firstName', 'N/A')
        last_name = user.get('profile', {}).get('lastName', 'N/A')
        
        print(f"   👤 {first_name} {last_name}")
        print(f"      user_id: {user.get('user_id', 'N/A')}")
        print(f"      password_hash: {'✅ Présent' if user.get('password_hash') else '❌ Absent'}")
        
        # Profil
        profile = user.get('profile', {})
        if profile:
            print(f"      profile:")
            print(f"         firstName: {profile.get('firstName', 'N/A')}")
            print(f"         lastName: {profile.get('lastName', 'N/A')}")
            print(f"         email: {profile.get('email', '❌ Absent')}")
            print(f"         age: {profile.get('age', 'N/A')}")
            print(f"         gender: {profile.get('gender', 'N/A')}")
            print(f"         weight: {profile.get('weight', 'N/A')}")
            print(f"         height: {profile.get('height', 'N/A')}")
            print(f"         bodyType: {profile.get('bodyType', 'N/A')}")
        else:
            print(f"      profile: ❌ Absent")
        
        print(f"      medical: {'✅ Présent' if user.get('medical') else '❌ Absent'}")
        print(f"      nutrition: {'✅ Présent' if user.get('nutrition') else '❌ Absent'}")
        print(f"      goals: {'✅ Présent' if user.get('goals') else '❌ Absent'}")
        print(f"      profile_completed: {user.get('profile_completed', False)}")
        
        # Vérifier les champs à supprimer
        if 'email' in user and user.get('email') is not None:
            print(f"      ⚠️  email (racine): {user['email']} - DEVRAIT ÊTRE SUPPRIMÉ")
        if 'username' in user:
            print(f"      ⚠️  username: {user['username']} - DEVRAIT ÊTRE SUPPRIMÉ")
        
        print()
    
    # Vérifier qu'il n'y a plus d'email ou username à la racine
    users_with_root_email = await user_collection.count_documents({"email": {"$exists": True}})
    users_with_username = await user_collection.count_documents({"username": {"$exists": True}})
    
    print(f"\n📊 Statistiques finales:")
    print(f"   - Utilisateurs avec 'email' à la racine: {users_with_root_email}")
    print(f"   - Utilisateurs avec 'username': {users_with_username}")
    
    if users_with_root_email == 0 and users_with_username == 0:
        print(f"\n✅ Migration réussie ! Le schéma est maintenant propre.")
    else:
        print(f"\n⚠️  Certains utilisateurs ont encore des champs à nettoyer.")
    
    print(f"\n" + "=" * 80)
    print("  OPÉRATION TERMINÉE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(reorganize_user_schema())
