"""
Script de test pour l'authentification.
Teste l'inscription et la connexion des utilisateurs.
"""

import requests
import json
from datetime import datetime


API_BASE_URL = "http://localhost:8000/api"


def print_banner(text):
    """Affiche un bandeau."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def test_register():
    """Test d'inscription d'un nouvel utilisateur."""
    print("[TEST 1] Inscription d'un nouvel utilisateur")
    print("-" * 60)
    
    # Générer un email unique
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "email": f"test_{timestamp}@example.com",
        "password": "password123",
        "username": f"TestUser{timestamp}"
    }
    
    print(f"Email:    {test_user['email']}")
    print(f"Username: {test_user['username']}")
    print(f"Password: {test_user['password']}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=test_user,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ INSCRIPTION RÉUSSIE!")
            print(f"   User ID:       {data['user_id']}")
            print(f"   Session Token: {data['session_token'][:40]}...")
            print(f"   Message:       {data['message']}")
            return data, test_user
        else:
            print(f"❌ ERREUR {response.status_code}")
            print(f"   {response.json()}")
            return None, test_user
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None, test_user


def test_login(test_user):
    """Test de connexion avec un utilisateur existant."""
    print("\n[TEST 2] Connexion avec l'utilisateur créé")
    print("-" * 60)
    
    print(f"Email:    {test_user['email']}")
    print(f"Password: {test_user['password']}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": test_user['email'],
                "password": test_user['password']
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CONNEXION RÉUSSIE!")
            print(f"   User ID:       {data['user_id']}")
            print(f"   Username:      {data['username']}")
            print(f"   Session Token: {data['session_token'][:40]}...")
            return data
        else:
            print(f"❌ ERREUR {response.status_code}")
            print(f"   {response.json()}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None


def test_wrong_password(test_user):
    """Test de connexion avec un mauvais mot de passe."""
    print("\n[TEST 3] Connexion avec un mauvais mot de passe")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": test_user['email'],
                "password": "mauvais_mot_de_passe"
            },
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ ERREUR CORRECTEMENT DÉTECTÉE!")
            print(f"   Message: {response.json()['detail']}")
            return True
        else:
            print(f"❌ Devrait retourner une erreur 401")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_duplicate_email(test_user):
    """Test d'inscription avec un email déjà utilisé."""
    print("\n[TEST 4] Inscription avec un email déjà utilisé")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json={
                "email": test_user['email'],
                "password": "password123",
                "username": "AutreUsername"
            },
            timeout=5
        )
        
        if response.status_code == 400:
            print("✅ ERREUR CORRECTEMENT DÉTECTÉE!")
            print(f"   Message: {response.json()['detail']}")
            return True
        else:
            print(f"❌ Devrait retourner une erreur 400")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_check_email(email):
    """Test de vérification de disponibilité d'email."""
    print("\n[TEST 5] Vérification de disponibilité d'email")
    print("-" * 60)
    
    try:
        # Email déjà utilisé
        response = requests.get(
            f"{API_BASE_URL}/auth/check-email/{email}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vérification pour: {email}")
            print(f"   Disponible: {data['available']}")
            
            if not data['available']:
                print("   ✅ Correct - Email déjà utilisé")
        
        # Email disponible
        response = requests.get(
            f"{API_BASE_URL}/auth/check-email/nouveau@example.com",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Vérification pour: nouveau@example.com")
            print(f"   Disponible: {data['available']}")
            
            if data['available']:
                print("   ✅ Correct - Email disponible")
                
        return True
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def test_session_usage(session_token):
    """Test d'utilisation du token de session."""
    print("\n[TEST 6] Utilisation du token de session")
    print("-" * 60)
    
    try:
        headers = {"X-Session-Token": session_token}
        
        response = requests.get(
            f"{API_BASE_URL}/session/info",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ TOKEN VALIDE!")
            print(f"   User ID:       {data['user_id']}")
            print(f"   Créée le:      {data['created_at']}")
            print(f"   Dernière activité: {data['last_activity']}")
            return True
        else:
            print(f"❌ ERREUR {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False


def main():
    print_banner("🔐 Tests d'Authentification")
    
    # Vérifier que le serveur est actif
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Serveur actif\n")
        else:
            print("❌ Serveur non accessible")
            return
    except:
        print("❌ Serveur non accessible. Démarrez-le avec: python run.py\n")
        return
    
    # Test 1: Inscription
    user_data, test_user = test_register()
    if not user_data:
        print("\n⚠️  Impossible de continuer les tests sans inscription réussie")
        return
    
    # Test 2: Connexion
    login_data = test_login(test_user)
    
    # Test 3: Mauvais mot de passe
    test_wrong_password(test_user)
    
    # Test 4: Email déjà utilisé
    test_duplicate_email(test_user)
    
    # Test 5: Vérification email
    test_check_email(test_user['email'])
    
    # Test 6: Utilisation de la session
    if user_data:
        test_session_usage(user_data['session_token'])
    
    # Résumé
    print_banner("✨ Tests Terminés")
    print("Compte de test créé:")
    print(f"  Email:    {test_user['email']}")
    print(f"  Password: {test_user['password']}")
    print(f"  User ID:  {user_data['user_id']}")
    print(f"\n💡 Vous pouvez vous connecter avec ce compte sur la page test_auth.html")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur\n")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}\n")
        import traceback
        traceback.print_exc()
