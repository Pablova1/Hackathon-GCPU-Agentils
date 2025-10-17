"""
Test rapide du mapping des slots vers le profil utilisateur
"""
from app.api.onboarding import map_minimal_slots_to_full_profile
import json

# Test 1: Slots obligatoires uniquement
print("="*70)
print("TEST 1: Slots obligatoires uniquement")
print("="*70)

slots_basic = {
    "firstName": "Jean",
    "lastName": "Dupont",
    "birthDate": "1990-05-15",
    "gender": "Male",
    "heightCm": 180,
    "weightKg": 75.5,
    "dietType": "omnivore",
    "activityLevel": "moderate",
}

result_basic = map_minimal_slots_to_full_profile(slots_basic)

print("\n📊 Résultat du mapping:")
print(json.dumps(result_basic, indent=2, ensure_ascii=False))

# Test 2: Avec réponses IA
print("\n" + "="*70)
print("TEST 2: Avec réponses IA")
print("="*70)

slots_with_ai = {
    "firstName": "Sophie",
    "lastName": "Martin",
    "birthDate": "1992-08-20",
    "gender": "Female",
    "heightCm": 168,
    "weightKg": 62.0,
    "dietType": "vegetarian",
    "activityLevel": "high",
    "ai_followup_0": "Je fais du yoga 3 fois par semaine",
    "ai_followup_1": "J'adore les smoothies verts et les salades composées",
    "ai_followup_2": "Mon objectif est d'améliorer ma souplesse",
}

result_with_ai = map_minimal_slots_to_full_profile(slots_with_ai)

print("\n📊 Résultat du mapping:")
print(json.dumps(result_with_ai, indent=2, ensure_ascii=False))

print("\n" + "="*70)
print("VÉRIFICATIONS")
print("="*70)

# Vérifier que les champs obligatoires sont bien remplis
checks = [
    ("firstName présent", result_with_ai.get("firstName") == "Sophie"),
    ("lastName présent", result_with_ai.get("lastName") == "Martin"),
    ("gender présent", result_with_ai.get("gender") == "Female"),
    ("age calculé", result_with_ai.get("age") > 0),
    ("activityLevel présent", result_with_ai.get("activityLevel") == "high"),
    ("diet présent", result_with_ai.get("diet") == "vegetarian"),
    ("notes avec réponses IA", result_with_ai.get("notes") is not None),
    ("notes contient 'ai_followup'", "ai_followup" in result_with_ai.get("notes", "")),
]

print()
for check_name, check_result in checks:
    status = "✅" if check_result else "❌"
    print(f"{status} {check_name}")

print("\n💡 Notes (réponses IA):")
print(f"   {result_with_ai.get('notes', 'Aucune')}")

print("\n🎉 Test terminé!")
