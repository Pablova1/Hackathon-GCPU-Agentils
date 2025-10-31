"""
Script pour vérifier la structure des documents utilisateurs.
"""

import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.db.mongo_client import get_database

async def check_user_structure():
    """Vérifie la structure des documents utilisateurs."""
    
    print("\n" + "="*80)
    print("🔍 STRUCTURE DES DOCUMENTS UTILISATEURS")
    print("="*80 + "\n")
    
    try:
        db = await get_database()
        users_collection = db["user"]
        
        # Récupérer le premier utilisateur
        user = await users_collection.find_one({})
        
        if not user:
            print("❌ Aucun utilisateur trouvé")
            return
        
        print("📋 Clés présentes dans le document utilisateur:")
        for key in user.keys():
            value = user[key]
            value_type = type(value).__name__
            
            if isinstance(value, dict):
                print(f"   • {key} ({value_type}) - Sous-clés: {list(value.keys())[:5]}")
            elif isinstance(value, list):
                print(f"   • {key} ({value_type}) - Longueur: {len(value)}")
            else:
                print(f"   • {key} ({value_type}) - Valeur: {str(value)[:50]}")
        
        print("\n" + "="*80)
        print(f"📄 Document complet (premier utilisateur):")
        print("="*80)
        import json
        print(json.dumps(user, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_structure())
