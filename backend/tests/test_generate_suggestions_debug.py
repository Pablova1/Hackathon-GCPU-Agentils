"""
Test pour déboguer la génération de suggestions
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database
from app.ai.agents.agent_initializer import (
    get_meal_suggestion_agent,
    get_coach_agent,
    get_medical_agent,
    get_orchestrator_agent
)


async def test_generate_suggestions():
    """Test de génération de suggestions pour un utilisateur"""
    
    db = await get_database()
    users_collection = db["user"]
    meals_collection = db["meals"]
    
    # Trouver un utilisateur avec profile_completed = True
    print("\n🔍 Recherche d'un utilisateur avec profil complet...\n")
    user = await users_collection.find_one({"profile_completed": True})
    
    if not user:
        print("❌ Aucun utilisateur avec profil complet trouvé")
        return
    
    user_id = user.get("user_id")
    email = user.get("profile", {}).get("email", "N/A")
    first_name = user.get("profile", {}).get("firstName", "N/A")
    
    print(f"✅ Utilisateur trouvé:")
    print(f"   - User ID: {user_id}")
    print(f"   - Nom: {first_name}")
    print(f"   - Email: {email}")
    
    # Vérifier les repas
    meal_count = await meals_collection.count_documents({"userId": user_id})
    print(f"   - Nombre de repas: {meal_count}")
    
    if meal_count == 0:
        print("\n⚠️  Aucun repas scanné pour cet utilisateur")
        print("   Voulez-vous continuer quand même ? (o/n)")
        response = input("> ")
        if response.lower() != 'o':
            return
    
    print(f"\n{'='*60}")
    print("🤖 Initialisation des agents...")
    print(f"{'='*60}\n")
    
    try:
        meal_agent = get_meal_suggestion_agent()
        print("✅ MealSuggestionAgent initialisé")
        
        coach_agent = get_coach_agent()
        print("✅ CoachAgent initialisé")
        
        medical_agent = get_medical_agent()
        print("✅ MedicalAgent initialisé")
        
        orchestrator = get_orchestrator_agent()
        print("✅ OrchestratorAgent initialisé")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation des agents: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'='*60}")
    print("🍽️  Génération de la suggestion de repas...")
    print(f"{'='*60}\n")
    
    try:
        meal_result = await meal_agent.generate_suggestions(user_id=user_id, days=7)
        
        if meal_result.get("success"):
            print("✅ Suggestion de repas générée avec succès")
            print(f"   Suggestion: {meal_result.get('suggestion', 'N/A')}")
        else:
            print(f"❌ Erreur lors de la génération de suggestion de repas:")
            print(f"   {meal_result.get('error')}")
            return
            
    except Exception as e:
        print(f"❌ Exception lors de la génération de suggestion de repas: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'='*60}")
    print("💪 Génération de la suggestion d'entraînement...")
    print(f"{'='*60}\n")
    
    try:
        workout_result = await coach_agent.generate_suggestions(user_id=user_id, days=7)
        
        if workout_result.get("success"):
            print("✅ Suggestion d'entraînement générée avec succès")
            print(f"   Suggestion: {workout_result.get('suggestion', 'N/A')}")
        else:
            print(f"❌ Erreur lors de la génération de suggestion d'entraînement:")
            print(f"   {workout_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception lors de la génération de suggestion d'entraînement: {e}")
        import traceback
        traceback.print_exc()
        workout_result = {"success": False, "error": str(e)}
    
    print(f"\n{'='*60}")
    print("🏥 Analyse du contexte médical (optionnel)...")
    print(f"{'='*60}\n")
    
    medical_result = None
    try:
        medical_result = await medical_agent.analyze_medical_context(user_id=user_id)
        
        if medical_result.get("success"):
            print("✅ Contexte médical analysé avec succès")
        else:
            print(f"⚠️  Pas de contexte médical disponible")
            medical_result = None
            
    except Exception as e:
        print(f"⚠️  Exception lors de l'analyse médicale (non bloquant): {e}")
        medical_result = None
    
    print(f"\n{'='*60}")
    print("🎼 Orchestration des suggestions...")
    print(f"{'='*60}\n")
    
    try:
        unified_result = orchestrator.orchestrate(
            meal_suggestion=meal_result,
            workout_suggestion=workout_result,
            medical_context=medical_result
        )
        
        if unified_result.get("success"):
            print("✅ Orchestration réussie !\n")
            print(f"💪 Message de motivation:")
            print(f"   {unified_result.get('motivation_message', 'N/A')}\n")
            
            meal_suggestions = unified_result.get("meal_suggestions", [])
            print(f"🍽️  Suggestions de repas ({len(meal_suggestions)}):")
            for i, meal in enumerate(meal_suggestions, 1):
                print(f"   {i}. {meal}")
            
            print(f"\n📊 Sauvegarde dans la base de données...")
            
            # Sauvegarder dans la base
            last_suggestion = {
                "motivation_message": unified_result.get("motivation_message"),
                "meal_suggestions": unified_result.get("meal_suggestions"),
                "individual_suggestions": unified_result.get("individual_suggestions"),
                "generated_at": unified_result.get("generated_at"),
                "status": "completed"
            }
            
            await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_suggestion": last_suggestion}}
            )
            
            print("✅ Suggestions sauvegardées avec succès !")
            
        else:
            print(f"❌ Erreur lors de l'orchestration:")
            print(f"   {unified_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Exception lors de l'orchestration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_generate_suggestions())
