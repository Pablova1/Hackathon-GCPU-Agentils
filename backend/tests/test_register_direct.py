"""
Test direct de la route d'inscription
"""
import requests
import json

def test_register():
    """Test d'inscription d'un nouvel utilisateur"""
    url = "http://localhost:8000/api/auth/register"
    
    data = {
        "email": "testdirect@example.com",
        "password": "test123456",
        "first_name": "Direct",
        "last_name": "Test"
    }
    
    print("🧪 Test d'inscription")
    print(f"📍 URL: {url}")
    print(f"📤 Données: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=data)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
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
    test_register()
