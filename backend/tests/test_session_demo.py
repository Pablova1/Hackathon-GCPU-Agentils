"""
Script de démonstration du système de sessions.
Teste la création de session et le tracking des analyses.
"""

import requests
import json
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Affiche un titre de section."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def main():
    print("🔐 Démonstration du système de sessions")
    
    # 1. Créer une session
    print_section("1. Création d'une session")
    
    response = requests.post(
        f"{API_BASE_URL}/session/create",
        json={"user_id": "demo_user_123"}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        session_token = session_data["session_token"]
        user_id = session_data["user_id"]
        
        print(f"✅ Session créée avec succès!")
        print(f"   Session Token: {session_token}")
        print(f"   User ID: {user_id}")
    else:
        print(f"❌ Erreur lors de la création: {response.text}")
        return
    
    # Headers pour les requêtes suivantes
    headers = {"X-Session-Token": session_token}
    
    # 2. Vérifier les informations de session
    print_section("2. Informations de la session")
    
    response = requests.get(
        f"{API_BASE_URL}/session/info",
        headers=headers
    )
    
    if response.status_code == 200:
        info = response.json()
        print(f"✅ Session valide")
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erreur: {response.text}")
    
    # 3. Valider la session
    print_section("3. Validation de la session")
    
    response = requests.post(
        f"{API_BASE_URL}/session/validate",
        headers=headers
    )
    
    if response.status_code == 200:
        validation = response.json()
        print(f"✅ {validation['message']}")
    else:
        print(f"❌ Session invalide: {response.text}")
    
    # 4. Simuler une analyse (si vous avez une image de test)
    print_section("4. Exemple d'analyse avec session")
    
    print("Pour analyser une assiette, utilisez :")
    print(f"  curl -X POST '{API_BASE_URL}/analyze/plate' \\")
    print(f"       -H 'X-Session-Token: {session_token}' \\")
    print(f"       -F 'file=@votre_image.jpg'")
    
    # 5. Consulter les statistiques
    print_section("5. Statistiques utilisateur")
    
    response = requests.get(
        f"{API_BASE_URL}/session/stats/{user_id}"
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Statistiques pour {user_id}:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print(f"⚠️  Pas encore de statistiques: {response.text}")
    
    # 6. Historique des analyses
    print_section("6. Historique des analyses")
    
    response = requests.get(
        f"{API_BASE_URL}/analyze/history?limit=5",
        headers=headers
    )
    
    if response.status_code == 200:
        history = response.json()
        if history["total"] == 0:
            print("📭 Aucune analyse pour le moment")
        else:
            print(f"📊 {history['total']} analyse(s) trouvée(s):")
            print(json.dumps(history["analyses"], indent=2, ensure_ascii=False))
    else:
        print(f"⚠️  Erreur lors de la récupération: {response.text}")
    
    # Résumé
    print_section("✨ Résumé")
    print(f"""
Votre session a été créée avec succès !

🔑 Token de session: {session_token}
👤 User ID: {user_id}

Pour utiliser cette session dans vos requêtes, ajoutez le header:
    X-Session-Token: {session_token}

Routes disponibles avec cette session:
    • POST /api/analyze/plate        - Analyser une assiette
    • POST /api/analyze/nutrients    - Analyser les nutriments
    • GET  /api/analyze/history      - Voir l'historique d'analyses
    • GET  /api/session/info         - Info de la session
    
Les analyses seront automatiquement liées à votre utilisateur !
    """)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur est démarré sur http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
