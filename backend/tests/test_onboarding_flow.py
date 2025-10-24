"""
Script de test pour vérifier le flux onboarding complet.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_onboarding_flow():
    print("=== Test du flux d'onboarding ===\n")
    
    # 1. Créer un utilisateur de test
    print("1. Inscription d'un nouvel utilisateur...")
    register_data = {
        "first_name": "Test",
        "last_name": "Onboarding",
        "email": f"test_onboarding_{int(requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC').json()['unixtime'])}@test.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("user_id")
            session_token = data.get("session_token")
            print(f"   ✓ Utilisateur créé: {user_id}")
            print(f"   ✓ Session token: {session_token[:20]}...")
        else:
            print(f"   ✗ Erreur: {response.json()}")
            return
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return
    
    # 2. Vérifier le statut du profil
    print("\n2. Vérification du statut du profil...")
    try:
        response = requests.get(f"{BASE_URL}/api/profile/check?user_id={user_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Profile completed: {data.get('profile_completed')}")
            print(f"   User exists: {data.get('user_exists')}")
            
            if data.get('profile_completed'):
                print("   ✗ Le profil ne devrait pas être complété après l'inscription!")
                return
            else:
                print("   ✓ Profil non complété (comme attendu)")
        else:
            print(f"   ✗ Erreur: {response.json()}")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
    
    # 3. Démarrer l'onboarding
    print("\n3. Démarrage de l'onboarding...")
    try:
        response = requests.post(f"{BASE_URL}/api/onboarding/start?user_id={user_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            first_question = data.get("question")
            print(f"   ✓ Session créée: {session_id}")
            print(f"   ✓ Première question: {first_question.get('text')}")
            print(f"     Slot: {first_question.get('slot')}")
            print(f"     Type: {first_question.get('type')}")
        else:
            print(f"   ✗ Erreur: {response.json()}")
            return
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return
    
    print("\n=== Test terminé avec succès! ===")
    print("\nProchaines étapes manuelles:")
    print("1. Démarrer le frontend: cd frontend && npm run dev")
    print("2. Ouvrir http://localhost:3000/onboarding")
    print("3. Se connecter avec:")
    print(f"   Email: {register_data['email']}")
    print(f"   Password: {register_data['password']}")

if __name__ == "__main__":
    test_onboarding_flow()
