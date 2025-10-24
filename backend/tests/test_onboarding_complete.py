"""
Test de la nouvelle route de soumission complète de l'onboarding
"""
import requests
import json

def test_submit_all_onboarding():
    """Test de soumission complète de toutes les réponses"""
    url = "http://localhost:8000/api/onboarding/submit-all"
    
    data = {
        "user_id": "user_test_complete",
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
    
    print("🧪 Test de soumission complète de l'onboarding")
    print(f"📍 URL: {url}")
    print(f"📤 Données: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=data)
        
        print(f"📥 Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCÈS!")
            print(f"📥 Réponse: {json.dumps(result, indent=2)}")
        else:
            print("❌ ÉCHEC!")
            print(f"📥 Réponse: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("Vérifiez que le backend est démarré sur http://localhost:8000")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_submit_all_onboarding()
