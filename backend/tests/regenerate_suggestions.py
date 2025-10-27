"""
Script pour régénérer les suggestions d'un utilisateur
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database
from app.api.routes.suggestions import generate_and_store_suggestions


async def regenerate_suggestions():
    """Régénère les suggestions pour un utilisateur spécifique"""
    
    user_id = "user_e48cd15f9038d6a2"
    
    db = await get_database()
    users_collection = db["user"]
    
    print(f"\n{'='*70}")
    print(f"🔄 Régénération des suggestions pour {user_id}")
    print(f"{'='*70}\n")
    
    # Récupérer l'utilisateur
    user = await users_collection.find_one({"user_id": user_id})
    
    if not user:
        print(f"❌ Utilisateur non trouvé")
        return
    
    name = f"{user.get('profile', {}).get('firstName', 'N/A')} {user.get('profile', {}).get('lastName', 'N/A')}"
    print(f"✅ Utilisateur trouvé: {name}")
    
    # Vérifier l'ancienne suggestion
    old_suggestion = user.get("last_suggestion")
    if old_suggestion:
        print(f"\n📊 Ancienne suggestion:")
        print(f"   Status: {old_suggestion.get('status')}")
        if old_suggestion.get('status') == 'failed':
            print(f"   Erreur: {old_suggestion.get('error')}")
    
    # Nettoyer l'ancienne suggestion
    print(f"\n🧹 Nettoyage de l'ancienne suggestion...")
    await users_collection.update_one(
        {"user_id": user_id},
        {"$unset": {"last_suggestion": ""}}
    )
    print(f"✅ Ancienne suggestion supprimée")
    
    # Générer une nouvelle suggestion
    print(f"\n🚀 Génération d'une nouvelle suggestion...")
    print(f"   (Cela peut prendre 10-20 secondes...)\n")
    
    try:
        await generate_and_store_suggestions(user_id, history_days=7)
        print(f"\n✅ Nouvelle suggestion générée avec succès!")
        
        # Vérifier le résultat
        updated_user = await users_collection.find_one({"user_id": user_id})
        new_suggestion = updated_user.get("last_suggestion")
        
        if new_suggestion:
            print(f"\n📊 Nouvelle suggestion:")
            print(f"   Status: {new_suggestion.get('status')}")
            
            if new_suggestion.get('status') == 'completed':
                motivation = new_suggestion.get('motivation_message', '')
                print(f"   💪 Motivation: {motivation}")
                
                meal_count = len(new_suggestion.get('meal_suggestions', []))
                print(f"   🍽️  Suggestions de repas: {meal_count}")
                
            elif new_suggestion.get('status') == 'failed':
                print(f"   ❌ Erreur: {new_suggestion.get('error')}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(regenerate_suggestions())
