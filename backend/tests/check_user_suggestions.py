"""
Script pour vérifier les suggestions d'un utilisateur
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database


async def check_user_suggestions():
    """Vérifie les suggestions pour tous les utilisateurs"""
    
    db = await get_database()
    users_collection = db["user"]
    
    print("\n" + "="*70)
    print("📊 Vérification des suggestions pour tous les utilisateurs")
    print("="*70 + "\n")
    
    # Trouver tous les utilisateurs
    users = await users_collection.find({}).to_list(length=100)
    
    users_with_suggestions = []
    users_without_suggestions = []
    
    for user in users:
        user_id = user.get("user_id")
        if not user_id:
            continue
            
        first_name = user.get("profile", {}).get("firstName", "N/A")
        last_name = user.get("profile", {}).get("lastName", "N/A")
        email = user.get("profile", {}).get("email", user.get("email", "N/A"))
        
        last_suggestion = user.get("last_suggestion")
        
        user_info = {
            "user_id": user_id,
            "name": f"{first_name} {last_name}",
            "email": email,
            "suggestion": last_suggestion
        }
        
        if last_suggestion:
            users_with_suggestions.append(user_info)
        else:
            users_without_suggestions.append(user_info)
    
    print(f"✅ Utilisateurs AVEC suggestions: {len(users_with_suggestions)}")
    print(f"❌ Utilisateurs SANS suggestions: {len(users_without_suggestions)}")
    print()
    
    if users_with_suggestions:
        print("\n" + "="*70)
        print("✅ Utilisateurs avec suggestions:")
        print("="*70 + "\n")
        
        for u in users_with_suggestions:
            print(f"👤 {u['name']}")
            print(f"   📧 {u['email']}")
            print(f"   🆔 {u['user_id']}")
            
            status = u['suggestion'].get('status', 'N/A')
            print(f"   📊 Status: {status}")
            
            if status == 'completed':
                motivation = u['suggestion'].get('motivation_message', '')
                if motivation:
                    print(f"   💪 Motivation: {motivation[:80]}...")
                
                meal_count = len(u['suggestion'].get('meal_suggestions', []))
                print(f"   🍽️  Suggestions de repas: {meal_count}")
            
            elif status == 'failed':
                error = u['suggestion'].get('error', 'N/A')
                print(f"   ❌ Erreur: {error}")
            
            elif status == 'generating':
                print(f"   ⏳ En cours de génération...")
            
            print()
    
    if users_without_suggestions:
        print("\n" + "="*70)
        print("❌ Utilisateurs SANS suggestions:")
        print("="*70 + "\n")
        
        for u in users_without_suggestions:
            print(f"👤 {u['name']}")
            print(f"   📧 {u['email']}")
            print(f"   🆔 {u['user_id']}")
            print()


if __name__ == "__main__":
    asyncio.run(check_user_suggestions())
