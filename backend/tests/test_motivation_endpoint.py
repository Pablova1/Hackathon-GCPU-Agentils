"""
Test de l'endpoint /suggestions/motivation/{user_id}
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.user_store import get_user_document


async def test_motivation_endpoint():
    """Test de l'endpoint motivation"""
    
    user_id = "user_e48cd15f9038d6a2"
    
    print(f"\n🔍 Test de l'endpoint /suggestions/motivation/{user_id}\n")
    
    try:
        # Récupérer l'utilisateur
        user = await get_user_document(user_id)
        
        if not user:
            print(f"❌ Utilisateur non trouvé: {user_id}")
            return
        
        print(f"✅ Utilisateur trouvé")
        print(f"   - Nom: {user.get('profile', {}).get('firstName', 'N/A')} {user.get('profile', {}).get('lastName', 'N/A')}")
        
        # Vérifier last_suggestion
        last_suggestion = user.get("last_suggestion")
        
        print(f"\n📊 last_suggestion:")
        if last_suggestion:
            print(f"   Type: {type(last_suggestion)}")
            print(f"   Contenu: {last_suggestion}")
            
            status = last_suggestion.get("status") if isinstance(last_suggestion, dict) else None
            print(f"\n   Status: {status}")
            
            if status == "completed":
                motivation = last_suggestion.get("motivation_message", "N/A")
                print(f"   Motivation: {motivation}")
                
            elif status == "failed":
                error = last_suggestion.get("error", "N/A")
                print(f"   Erreur: {error}")
                
        else:
            print("   ❌ Aucune suggestion")
            
        # Simuler la réponse de l'API
        print(f"\n📤 Réponse simulée de l'API:")
        
        if not last_suggestion:
            response = {
                "motivation_message": "Keep scanning your meals! We'll provide personalized suggestions soon.",
                "status": "no_suggestion_yet",
                "generated_at": None
            }
        elif isinstance(last_suggestion, dict) and last_suggestion.get("status") == "failed":
            response = {
                "motivation_message": "We're working on your suggestions. Please try again later.",
                "status": "failed",
                "generated_at": last_suggestion.get("generated_at")
            }
        elif isinstance(last_suggestion, dict):
            response = {
                "motivation_message": last_suggestion.get("motivation_message", "Keep up the great work!"),
                "status": "completed",
                "generated_at": last_suggestion.get("generated_at")
            }
        else:
            response = {
                "motivation_message": "Error: Invalid suggestion format",
                "status": "error",
                "generated_at": None
            }
        
        print(f"   {response}")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_motivation_endpoint())
