"""
Script pour vérifier l'état des suggestions dans la base de données.
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le dossier backend au path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.db.user_store import get_user_document
from app.db.meal_store import get_meals_by_user_id
from app.db.mongo_client import get_database

async def check_suggestions_status():
    """Vérifie l'état des suggestions pour tous les utilisateurs."""
    
    print("\n" + "="*80)
    print("🔍 VÉRIFICATION DE L'ÉTAT DES SUGGESTIONS")
    print("="*80 + "\n")
    
    try:
        # Récupérer tous les utilisateurs
        db = await get_database()
        users_collection = db["user"]
        users = await users_collection.find({}).to_list(length=None)
        
        if not users:
            print("❌ Aucun utilisateur trouvé dans la base de données")
            return
        
        print(f"📊 Nombre d'utilisateurs trouvés: {len(users)}\n")
        
        for user in users:
            user_id = str(user.get('_id'))
            username = user.get('username', 'N/A')
            email = user.get('email', 'N/A')
            
            print(f"\n{'─'*80}")
            print(f"👤 Utilisateur: {username} ({email})")
            print(f"   ID: {user_id}")
            print(f"{'─'*80}")
            
            # Vérifier les repas scannés
            meals = await get_meals_by_user_id(user_id)
            print(f"🍽️  Repas scannés: {len(meals)}")
            
            if meals:
                latest_meal = max(meals, key=lambda m: m.get('created_at', ''))
                print(f"   Dernier repas: {latest_meal.get('created_at', 'N/A')}")
            
            # Vérifier les suggestions
            last_suggestion = user.get('last_suggestion')
            
            if not last_suggestion:
                print("❌ Aucune suggestion générée")
                print("   💡 Solution: Scannez un nouveau repas pour déclencher la génération")
            else:
                status = last_suggestion.get('status', 'unknown')
                generated_at = last_suggestion.get('generated_at', 'N/A')
                
                print(f"\n📋 État des suggestions:")
                print(f"   Status: {status}")
                print(f"   Généré le: {generated_at}")
                
                if status == "completed":
                    meal_suggestions = last_suggestion.get('meal_suggestions', [])
                    motivation = last_suggestion.get('motivation_message', 'N/A')
                    
                    print(f"   ✅ Suggestions de repas: {len(meal_suggestions)}")
                    print(f"   💬 Message de motivation: {motivation[:100]}..." if len(motivation) > 100 else f"   💬 Message de motivation: {motivation}")
                    
                    if meal_suggestions:
                        print(f"\n   📝 Aperçu des suggestions:")
                        for i, suggestion in enumerate(meal_suggestions[:3], 1):
                            print(f"      {i}. {suggestion.get('name', 'N/A')} ({suggestion.get('meal_time', 'N/A')})")
                
                elif status == "generating":
                    print("   ⏳ Génération en cours...")
                    print("   💡 Attendez quelques secondes et réessayez")
                
                elif status == "failed":
                    error = last_suggestion.get('error', 'Unknown error')
                    print(f"   ❌ Échec de la génération")
                    print(f"   Erreur: {error}")
        
        print(f"\n{'='*80}")
        print("✅ Vérification terminée")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_suggestions_status())
