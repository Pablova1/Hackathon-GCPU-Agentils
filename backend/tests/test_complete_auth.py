"""
Script de test pour vérifier l'inscription et la connexion
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import requests
import json

API_URL = "http://localhost:8000/api"

def test_register():
    """Teste l'inscription d'un nouvel utilisateur."""
    print("=" * 80)
    print("  TEST D'INSCRIPTION")
    print("=" * 80)
    
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "password": "Test123!"
    }
    
    print(f"\n📤 Envoi de la requête d'inscription:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Réponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Inscription réussie!")
            return response.json()
        else:
            print(f"\n❌ Échec de l'inscription: {response.json().get('detail', 'Erreur inconnue')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return None


def test_login(email, password):
    """Teste la connexion d'un utilisateur."""
    print("\n" + "=" * 80)
    print("  TEST DE CONNEXION")
    print("=" * 80)
    
    payload = {
        "email": email,
        "password": password
    }
    
    print(f"\n📤 Envoi de la requête de connexion:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Réponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Connexion réussie!")
            return response.json()
        else:
            print(f"\n❌ Échec de la connexion: {response.json().get('detail', 'Erreur inconnue')}")
            return None
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return None


def test_session(session_token):
    """Teste une requête authentifiée."""
    print("\n" + "=" * 80)
    print("  TEST DE SESSION")
    print("=" * 80)
    
    print(f"\n📤 Test d'une requête avec session_token:")
    print(f"   Token: {session_token[:20]}...")
    
    try:
        response = requests.get(
            f"{API_URL}/session/info",
            headers={"X-Session-Token": session_token}
        )
        
        print(f"\n📥 Réponse (Status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Session valide!")
        else:
            print("\n❌ Session invalide")
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


def main():
    print("\n🧪 TESTS D'AUTHENTIFICATION\n")
    
    # Test 1: Inscription
    register_result = test_register()
    
    if register_result:
        session_token = register_result.get("session_token")
        email = register_result.get("email")
        
        # Test 2: Connexion avec le compte créé
        login_result = test_login(email, "Test123!")
        
        if login_result:
            # Test 3: Utiliser le token de session
            test_session(login_result.get("session_token"))
    
    # Test 4: Connexion avec un compte existant
    print("\n" + "=" * 80)
    print("  TEST AVEC COMPTE EXISTANT")
    print("=" * 80)
    
    existing_accounts = [
        ("tes@hotmail.com", "Test123!"),
        ("sophie.durand@test-hackathon.com", "Test123!"),
        ("sophie.martin@test-hackathon.com", "Test123!"),
    ]
    
    for email, password in existing_accounts:
        print(f"\n🔍 Test de connexion avec: {email}")
        result = test_login(email, password)
        if result:
            print(f"   ✅ Connexion réussie pour {result.get('first_name')} {result.get('last_name')}")
        else:
            print(f"   ❌ Échec de la connexion")
    
    print("\n" + "=" * 80)
    print("  FIN DES TESTS")
    print("=" * 80)


if __name__ == "__main__":
    print("\n⚠️  Assurez-vous que le serveur backend est démarré sur http://localhost:8000")
    input("\nAppuyez sur Entrée pour continuer...")
    main()
