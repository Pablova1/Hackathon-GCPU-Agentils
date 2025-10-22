"""
Script de nettoyage pour supprimer l'ancienne collection user_sessions.
À exécuter après la migration vers les sessions simplifiées.
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database


async def cleanup_old_sessions():
    """Supprime l'ancienne collection user_sessions si elle existe."""
    
    print("=" * 60)
    print("Nettoyage - Suppression de l'ancienne collection user_sessions")
    print("=" * 60)
    
    db = await get_database()
    
    # Vérifier si la collection existe
    collections = await db.list_collection_names()
    
    if "user_sessions" not in collections:
        print("\n✅ La collection 'user_sessions' n'existe pas.")
        print("   Aucune action nécessaire.")
        return
    
    # Compter les documents
    session_count = await db["user_sessions"].count_documents({})
    
    print(f"\n⚠️  Collection 'user_sessions' trouvée avec {session_count} document(s)")
    
    if session_count > 0:
        print("\n📋 Quelques exemples de sessions à supprimer:")
        sessions = await db["user_sessions"].find().limit(3).to_list(3)
        for i, sess in enumerate(sessions, 1):
            print(f"   {i}. User: {sess.get('user_id')}, Token: {sess.get('session_token', '')[:20]}...")
    
    # Demander confirmation
    print(f"\n❓ Voulez-vous supprimer la collection 'user_sessions' ?")
    print("   (Les utilisateurs devront se reconnecter)")
    
    response = input("   Taper 'OUI' pour confirmer: ")
    
    if response.strip().upper() != "OUI":
        print("\n❌ Opération annulée.")
        return
    
    # Supprimer la collection
    print("\n🗑️  Suppression en cours...")
    await db["user_sessions"].drop()
    
    # Vérifier
    collections_after = await db.list_collection_names()
    
    if "user_sessions" not in collections_after:
        print("✅ Collection 'user_sessions' supprimée avec succès!")
        print(f"   {session_count} session(s) ont été supprimées.")
        print("\n📝 Les utilisateurs devront se reconnecter pour obtenir un nouveau token.")
    else:
        print("❌ Erreur: La collection existe encore.")


if __name__ == "__main__":
    try:
        asyncio.run(cleanup_old_sessions())
    except KeyboardInterrupt:
        print("\n\n❌ Opération interrompue par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
