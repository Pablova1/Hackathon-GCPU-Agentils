"""
Test pour vérifier l'endpoint /profile/check
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database


async def test_profile_check():
    """Test de l'endpoint profile/check"""
    
    db = await get_database()
    users_collection = db["user"]
    
    # Lister tous les utilisateurs
    print("\n🔍 Recherche de tous les utilisateurs...\n")
    users = await users_collection.find().to_list(length=10)
    
    if not users:
        print("❌ Aucun utilisateur trouvé dans la base de données")
        return
    
    print(f"✅ {len(users)} utilisateur(s) trouvé(s)\n")
    
    for i, user in enumerate(users, 1):
        print(f"\n{'='*60}")
        print(f"Utilisateur #{i}")
        print(f"{'='*60}")
        
        user_id = user.get("user_id", "N/A")
        email = user.get("email", "N/A")
        username = user.get("username", "N/A")
        profile_completed = user.get("profile_completed", False)
        
        print(f"👤 User ID: {user_id}")
        print(f"📧 Email: {email}")
        print(f"🏷️  Username: {username}")
        print(f"✔️  Profile completed: {profile_completed}")
        
        # Vérifier le profil
        profile = user.get("profile", user.get("profil", {}))
        if profile:
            print(f"\n📋 Profil:")
            print(f"   - Prénom: {profile.get('firstName', profile.get('prenom', 'N/A'))}")
            print(f"   - Nom: {profile.get('lastName', profile.get('nom', 'N/A'))}")
            print(f"   - Âge: {profile.get('age', 'N/A')}")
            print(f"   - Poids: {profile.get('weight', profile.get('poids', 'N/A'))} kg")
            print(f"   - Taille: {profile.get('height', profile.get('taille', 'N/A'))} cm")
            print(f"   - Genre: {profile.get('gender', profile.get('sexe', 'N/A'))}")
            print(f"   - Morphologie: {profile.get('bodyType', profile.get('morphologie', 'N/A'))}")
        else:
            print(f"\n⚠️  Pas de profil détaillé")
        
        # Vérifier les objectifs
        goals = user.get("goals", user.get("objectifs", {}))
        if goals:
            print(f"\n🎯 Objectifs:")
            print(f"   - Perte de poids: {goals.get('weightLoss', goals.get('perte_de_poids', False))}")
            print(f"   - Gain musculaire: {goals.get('muscleGain', goals.get('masse_musculaire', False))}")
            print(f"   - Détail: {goals.get('goalDetail', goals.get('objectif_detail', 'N/A'))}")
        
        # Vérifier la nutrition
        nutrition = user.get("nutrition", user.get("alimentaire", {}))
        if nutrition:
            print(f"\n🥗 Nutrition:")
            print(f"   - Régime: {nutrition.get('diet', nutrition.get('regime', 'N/A'))}")
            print(f"   - Intolérances: {nutrition.get('intolerances', [])}")
        
        # Simulation de ce que l'API retourne
        print(f"\n🔧 Ce que l'API /profile/check retournerait:")
        print(f"   {{")
        print(f"      'profile_completed': {profile_completed},")
        print(f"      'user_exists': True,")
        print(f"      'profile': {profile}")
        print(f"   }}")


if __name__ == "__main__":
    asyncio.run(test_profile_check())
