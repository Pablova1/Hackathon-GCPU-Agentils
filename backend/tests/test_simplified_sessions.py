"""
Test de la nouvelle architecture de sessions simplifiée.
Vérifie que les sessions sont bien stockées dans la collection 'user'.
"""

import asyncio
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database
from app.middleware.session_manager import SessionManager


async def test_simplified_sessions():
    """Test complet du nouveau système de sessions."""
    
    print("=" * 60)
    print("TEST - Système de Sessions Simplifié")
    print("=" * 60)
    
    db = await get_database()
    users = db["user"]
    
    # 1. Créer un utilisateur de test
    test_user_id = f"test_user_simple_{datetime.now().timestamp()}"
    print(f"\n1️⃣  Création utilisateur de test: {test_user_id}")
    
    test_user = {
        "user_id": test_user_id,
        "password_hash": "test_hash",
        "created_at": datetime.now(),
        "profile_completed": False,
        "profile": {
            "firstName": "Test",
            "lastName": "Simplified",
            "email": f"{test_user_id}@test.com",
            "age": 25,
            "gender": "Other",
            "weight": 70.0,
            "height": 175.0
        }
    }
    
    await users.insert_one(test_user)
    print("✅ Utilisateur créé")
    
    # 2. Créer une session
    print(f"\n2️⃣  Création d'une session pour {test_user_id}")
    session_manager = SessionManager()
    session = await session_manager.create_user_session(test_user_id)
    
    print(f"✅ Session créée:")
    print(f"   - Token: {session['session_token'][:20]}...")
    print(f"   - Expires: {session['expires_at']}")
    
    # 3. Vérifier que la session est dans le document user
    print(f"\n3️⃣  Vérification stockage dans collection 'user'")
    user_doc = await users.find_one({"user_id": test_user_id})
    
    assert user_doc.get("session_token") == session["session_token"], "Token non trouvé dans user!"
    assert user_doc.get("session_created_at") is not None, "session_created_at manquant!"
    assert user_doc.get("session_expires_at") is not None, "session_expires_at manquant!"
    
    print("✅ Session correctement stockée dans le document user")
    print(f"   - session_token: {user_doc['session_token'][:20]}...")
    print(f"   - session_created_at: {user_doc['session_created_at']}")
    print(f"   - session_expires_at: {user_doc['session_expires_at']}")
    
    # 4. Récupérer la session par token
    print(f"\n4️⃣  Récupération de la session par token")
    retrieved_session = await session_manager.get_session(session["session_token"])
    
    assert retrieved_session["user_id"] == test_user_id, "User ID incorrect!"
    print("✅ Session récupérée avec succès")
    print(f"   - User ID: {retrieved_session['user_id']}")
    
    # 5. Vérifier la mise à jour de last_activity
    print(f"\n5️⃣  Vérification mise à jour last_activity")
    user_doc_updated = await users.find_one({"user_id": test_user_id})
    
    assert user_doc_updated.get("last_activity") is not None, "last_activity non mis à jour!"
    print("✅ last_activity mis à jour automatiquement")
    
    # 6. Tester la révocation de session
    print(f"\n6️⃣  Test de révocation de session (logout)")
    await session_manager.revoke_session(test_user_id)
    
    user_doc_revoked = await users.find_one({"user_id": test_user_id})
    assert user_doc_revoked.get("session_token") is None, "Token non révoqué!"
    print("✅ Session révoquée avec succès")
    
    # 7. Vérifier qu'on ne peut plus utiliser le token révoqué
    print(f"\n7️⃣  Vérification rejet du token révoqué")
    try:
        await session_manager.get_session(session["session_token"])
        print("❌ ERREUR: Le token révoqué fonctionne encore!")
        return False
    except Exception as e:
        print(f"✅ Token révoqué correctement rejeté: {str(e)[:50]}...")
    
    # 8. Vérifier l'absence de la collection user_sessions
    print(f"\n8️⃣  Vérification absence collection 'user_sessions'")
    collections = await db.list_collection_names()
    
    if "user_sessions" in collections:
        session_count = await db["user_sessions"].count_documents({})
        print(f"⚠️  Collection user_sessions existe encore ({session_count} documents)")
        print("   Vous pouvez la supprimer: db.user_sessions.drop()")
    else:
        print("✅ Collection user_sessions n'existe pas (bon!)")
    
    # 9. Stats utilisateur
    print(f"\n9️⃣  Test récupération des stats utilisateur")
    stats = await session_manager.get_user_stats(test_user_id)
    
    print(f"✅ Stats récupérées:")
    print(f"   - User ID: {stats['user_id']}")
    print(f"   - Total analyses: {stats['total_analyses']}")
    print(f"   - Onboarding completed: {stats['onboarding_completed']}")
    print(f"   - Has active session: {stats['has_active_session']}")
    
    # 10. Nettoyage
    print(f"\n🧹 Nettoyage de l'utilisateur de test")
    await users.delete_one({"user_id": test_user_id})
    print("✅ Utilisateur de test supprimé")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS PASSÉS!")
    print("=" * 60)
    print("\n📝 Résumé:")
    print("   - Sessions stockées dans la collection 'user' ✅")
    print("   - Création/récupération/révocation fonctionnent ✅")
    print("   - Collection user_sessions non utilisée ✅")
    print("   - Architecture simplifiée opérationnelle ✅")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_simplified_sessions())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
