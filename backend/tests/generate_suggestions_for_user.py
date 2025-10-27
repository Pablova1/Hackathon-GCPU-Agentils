"""
Script pour générer des suggestions pour un utilisateur spécifique
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database
from app.api.routes.suggestions import generate_and_store_suggestions


async def main():
    """Génère les suggestions pour un utilisateur spécifique"""
    
    db = await get_database()
    users_collection = db["user"]
    
    print("\n" + "="*60)
    print("🔍 Liste des utilisateurs avec profil complet")
    print("="*60 + "\n")
    
    # Trouver tous les utilisateurs avec profil complet
    users = await users_collection.find({"profile_completed": True}).to_list(length=20)
    
    if not users:
        print("❌ Aucun utilisateur avec profil complet trouvé")
        return
    
    print(f"Trouvé {len(users)} utilisateur(s):\n")
    
    for i, user in enumerate(users, 1):
        user_id = user.get("user_id", "❌ PAS DE USER_ID")
        email = user.get("profile", {}).get("email", user.get("email", "N/A"))
        first_name = user.get("profile", {}).get("firstName", "N/A")
        last_name = user.get("profile", {}).get("lastName", "N/A")
        
        print(f"{i}. {first_name} {last_name}")
        print(f"   📧 Email: {email}")
        print(f"   🆔 User ID: {user_id}")
        print()
    
    # Demander quel utilisateur
    print("Entrez le numéro de l'utilisateur pour lequel générer des suggestions (ou 'q' pour quitter):")
    choice = input("> ").strip()
    
    if choice.lower() == 'q':
        return
    
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(users):
            print("❌ Choix invalide")
            return
    except ValueError:
        print("❌ Veuillez entrer un nombre")
        return
    
    selected_user = users[index]
    user_id = selected_user.get("user_id")
    
    if not user_id:
        print("\n❌ Cet utilisateur n'a pas de user_id!")
        print("Voulez-vous lui en créer un ? (o/n)")
        response = input("> ").strip().lower()
        
        if response == 'o':
            import uuid
            new_user_id = f"user_{uuid.uuid4().hex[:16]}"
            await users_collection.update_one(
                {"_id": selected_user["_id"]},
                {"$set": {"user_id": new_user_id}}
            )
            user_id = new_user_id
            print(f"✅ User ID créé: {new_user_id}")
        else:
            return
    
    print(f"\n{'='*60}")
    print(f"🚀 Génération des suggestions pour {selected_user.get('profile', {}).get('firstName', 'Utilisateur')}")
    print(f"{'='*60}\n")
    
    try:
        await generate_and_store_suggestions(user_id, history_days=7)
        print("\n✅ Suggestions générées et stockées avec succès !")
        print(f"\nVous pouvez maintenant voir vos suggestions sur la page /suggestion")
        print(f"avec le user_id: {user_id}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
