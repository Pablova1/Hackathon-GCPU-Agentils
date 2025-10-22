"""
Test du flux complet : analyse d'assiette -> analyse nutritionnelle -> création de repas
"""
import sys
import os

# Ajouter le dossier backend au path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = f"test_meal_flow_{int(os.urandom(4).hex(), 16)}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "Test123!"

def test_complete_meal_flow():
    """Test le flux complet de création de repas via l'analyse"""
    
    print("\n" + "="*80)
    print("TEST: Flux complet d'analyse et création de repas")
    print("="*80)
    
    # 1. Créer un utilisateur de test
    print("\n1️⃣ Création d'un utilisateur de test...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    assert response.status_code == 200, f"Échec de l'inscription: {response.text}"
    
    session_token = response.json()["session_token"]
    user_id = response.json()["user_id"]
    print(f"   ✅ Utilisateur créé: {TEST_EMAIL}")
    print(f"   📝 Session token: {session_token[:20]}...")
    print(f"   🆔 User ID: {user_id}")
    
    # 2. Simuler une analyse d'assiette (sans vraie image, on utilise directement l'endpoint nutrients)
    print("\n2️⃣ Simulation d'une analyse nutritionnelle...")
    
    # Liste d'aliments fictifs
    aliments_data = [
        {"name": "poulet grillé", "estimated_quantity": 150},
        {"name": "riz complet", "estimated_quantity": 100},
        {"name": "brocoli", "estimated_quantity": 80}
    ]
    
    headers = {"X-Session-Token": session_token}
    response = requests.post(
        f"{BASE_URL}/api/analyze/nutrients",
        json=aliments_data,
        headers=headers
    )
    
    assert response.status_code == 200, f"Échec de l'analyse nutritionnelle: {response.text}"
    
    nutrient_result = response.json()
    print(f"   ✅ Analyse nutritionnelle réussie")
    print(f"   📊 Nutriments: {json.dumps(nutrient_result.get('nutrient_summary', {}), indent=6)}")
    
    # Vérifier que meal_id est présent dans la réponse
    assert "meal_id" in nutrient_result, "meal_id manquant dans la réponse"
    meal_id = nutrient_result["meal_id"]
    print(f"   🍽️ Repas créé avec ID: {meal_id}")
    
    # 3. Vérifier que le repas existe dans la collection meals
    print("\n3️⃣ Vérification que le repas est bien dans la collection meals...")
    
    response = requests.get(
        f"{BASE_URL}/meals/{meal_id}",
        headers=headers
    )
    
    assert response.status_code == 200, f"Échec de récupération du repas: {response.text}"
    
    meal = response.json()
    print(f"   ✅ Repas récupéré: {meal['name']}")
    print(f"   🥗 Ingrédients: {meal['ingredients']}")
    print(f"   💪 Calories: {meal['nutrients']['calories']} kcal")
    
    # 4. Vérifier que le repas apparaît dans les statistiques
    print("\n4️⃣ Vérification que le repas apparaît dans les statistiques...")
    
    response = requests.get(
        f"{BASE_URL}/meals/user/{user_id}/home-stats",
        headers=headers
    )
    
    assert response.status_code == 200, f"Échec de récupération des stats: {response.text}"
    
    stats = response.json()
    print(f"   ✅ Statistiques récupérées")
    print(f"   📈 Total de repas scannés: {stats['total_meals_scanned']}")
    print(f"   📅 Jours avec repas ce mois: {stats['current_month_calendar']['days_with_meals']}")
    print(f"   ⭐ Score hebdomadaire: {stats['weekly_score']['score']}/5")
    print(f"   💬 Commentaire: {stats['weekly_score']['comment']}")
    
    assert stats['total_meals_scanned'] >= 1, "Le repas n'apparaît pas dans les statistiques"
    
    # 5. Nettoyage : supprimer l'utilisateur de test
    print("\n5️⃣ Nettoyage...")
    response = requests.delete(
        f"{BASE_URL}/api/profile/delete",
        headers=headers
    )
    print(f"   🗑️ Utilisateur de test supprimé")
    
    print("\n" + "="*80)
    print("✅ TEST RÉUSSI : Le flux complet fonctionne correctement !")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_complete_meal_flow()
    except AssertionError as e:
        print(f"\n❌ TEST ÉCHOUÉ: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
