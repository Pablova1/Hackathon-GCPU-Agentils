"""
Test rapide de création d'un nouveau compte et connexion
"""

import requests
import json

API_URL = "http://localhost:8000/api"

print("🧪 TEST D'INSCRIPTION ET CONNEXION\n")

# Test 1: Inscription
print("=" * 60)
print("1️⃣  INSCRIPTION D'UN NOUVEAU COMPTE")
print("=" * 60)

register_payload = {
    "first_name": "Alice",
    "last_name": "Dupont",
    "email": "alice.dupont@example.com",
    "password": "MonMotDePasse123!"
}

print(f"\n📤 Inscription avec:")
print(f"   Prénom: {register_payload['first_name']}")
print(f"   Nom: {register_payload['last_name']}")
print(f"   Email: {register_payload['email']}")

response = requests.post(
    f"{API_URL}/auth/register",
    json=register_payload
)

print(f"\n📥 Réponse ({response.status_code}):")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Inscription réussie!")
    print(f"   User ID: {data['user_id']}")
    print(f"   Nom complet: {data['first_name']} {data['last_name']}")
    print(f"   Session Token: {data['session_token'][:30]}...")
    
    # Test 2: Connexion avec le même compte
    print("\n" + "=" * 60)
    print("2️⃣  CONNEXION AVEC LE COMPTE CRÉÉ")
    print("=" * 60)
    
    login_payload = {
        "email": register_payload['email'],
        "password": register_payload['password']
    }
    
    print(f"\n📤 Connexion avec: {login_payload['email']}")
    
    response2 = requests.post(
        f"{API_URL}/auth/login",
        json=login_payload
    )
    
    print(f"\n📥 Réponse ({response2.status_code}):")
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   ✅ Connexion réussie!")
        print(f"   Nom complet: {data2['first_name']} {data2['last_name']}")
        print(f"   Session Token: {data2['session_token'][:30]}...")
    else:
        print(f"   ❌ Échec: {response2.json()}")
        
else:
    print(f"   ❌ Échec: {response.json()}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS")
print("=" * 60)
