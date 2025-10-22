"""
Test de validation des données d'inscription
"""

import requests
import json

API_URL = "http://localhost:8000/api"

print("🧪 TEST DE VALIDATION\n")

# Test avec des données vides
print("=" * 60)
print("1️⃣  TEST AVEC DONNÉES VIDES")
print("=" * 60)

test_cases = [
    {
        "name": "Tous les champs remplis",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "Password123"
        }
    },
    {
        "name": "Email vide",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "",
            "password": "Password123"
        }
    },
    {
        "name": "Prénom vide",
        "data": {
            "first_name": "",
            "last_name": "User",
            "email": "test2@example.com",
            "password": "Password123"
        }
    },
    {
        "name": "Mot de passe court",
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test3@example.com",
            "password": "12345"
        }
    }
]

for test_case in test_cases:
    print(f"\n📤 {test_case['name']}:")
    print(f"   Données: {json.dumps(test_case['data'], indent=6)}")
    
    response = requests.post(
        f"{API_URL}/auth/register",
        json=test_case['data']
    )
    
    print(f"\n📥 Réponse ({response.status_code}):")
    try:
        data = response.json()
        print(f"   {json.dumps(data, indent=6, ensure_ascii=False)}")
    except:
        print(f"   {response.text}")
    
    print("\n" + "-" * 60)

print("\n✅ TESTS TERMINÉS")
