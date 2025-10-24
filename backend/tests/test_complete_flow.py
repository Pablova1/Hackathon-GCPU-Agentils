"""
Test complet: Inscription + Onboarding
"""
import requests
import json
import time

def test_complete_flow():
    """Test du flow complet inscription → onboarding"""
    
    # Étape 1: Inscription
    print("=" * 60)
    print("ÉTAPE 1: INSCRIPTION")
    print("=" * 60)
    
    register_url = "http://localhost:8000/api/auth/register"
    register_data = {
        "email": f"complete_test_{int(time.time())}@example.com",
        "password": "test123456",
        "first_name": "Jean",
        "last_name": "Dupont"
    }
    
    print(f"📍 URL: {register_url}")
    print(f"📤 Données: {json.dumps(register_data, indent=2)}")
    print()
    
    try:
        response = requests.post(register_url, json=register_data)
        print(f"📥 Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print("✅ Inscription réussie!")
            print(f"   User ID: {result['user_id']}")
            print(f"   Email: {result['email']}")
            print(f"   Nom: {result['first_name']} {result['last_name']}")
            user_id = result['user_id']
        else:
            print(f"❌ Échec: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    print()
    print("=" * 60)
    print("ÉTAPE 2: ONBOARDING (toutes les questions)")
    print("=" * 60)
    
    # Étape 2: Onboarding complet
    onboarding_url = "http://localhost:8000/api/onboarding/submit-all"
    onboarding_data = {
        "user_id": user_id,
        "answers": {
            "birthDate": "1990-05-15",
            "gender": "Male",
            "heightCm": 175,
            "weightKg": 70,
            "bodyType": "mesomorphic",
            "dietType": "omnivore",
            "activityLevel": "moderate"
        }
    }
    
    print(f"📍 URL: {onboarding_url}")
    print(f"📤 Données: {json.dumps(onboarding_data, indent=2)}")
    print()
    
    try:
        response = requests.post(onboarding_url, json=onboarding_data)
        print(f"📥 Status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print("✅ Onboarding réussi!")
            print(f"📥 Réponse: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Échec: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print()
    print("=" * 60)
    print("✨ TEST COMPLET TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_flow()
