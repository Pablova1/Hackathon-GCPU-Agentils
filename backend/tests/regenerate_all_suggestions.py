"""
Script pour régénérer les suggestions pour tous les utilisateurs qui ont des repas.
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.db.mongo_client import get_database
from app.api.routes.suggestions import generate_and_store_suggestions

async def regenerate_all_suggestions():
    """Régénère les suggestions pour tous les utilisateurs."""
    
    print("\n" + "="*80)
    print("🔄 RÉGÉNÉRATION DES SUGGESTIONS POUR TOUS LES UTILISATEURS")
    print("="*80 + "\n")
    
    try:
        # Récupérer tous les utilisateurs
        db = await get_database()
        users_collection = db["user"]
        users = await users_collection.find({}).to_list(length=None)
        
        if not users:
            print("❌ Aucun utilisateur trouvé")
            return
        
        print(f"📊 Nombre d'utilisateurs trouvés: {len(users)}\n")
        
        success_count = 0
        error_count = 0
        
        for user in users:
            user_id = str(user.get('_id'))
            username = user.get('username', 'N/A')
            
            print(f"👤 Traitement de l'utilisateur: {username} ({user_id})")
            
            try:
                # Générer les suggestions
                await generate_and_store_suggestions(user_id, history_days=7)
                print(f"   ✅ Suggestions générées avec succès\n")
                success_count += 1
                
                # Attendre un peu pour ne pas surcharger l'API Gemini
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Erreur: {str(e)}\n")
                error_count += 1
        
        print("="*80)
        print(f"✅ Régénération terminée")
        print(f"   Succès: {success_count}/{len(users)}")
        print(f"   Erreurs: {error_count}/{len(users)}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Erreur globale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(regenerate_all_suggestions())
