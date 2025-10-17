"""
Script de test complet du flux onboarding
Exécute : python test_onboarding.py
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Ajuste le port si nécessaire
USER_ID = "test_user_" + datetime.now().strftime("%Y%m%d_%H%M%S")

# Les réponses que tu veux donner aux 8 questions obligatoires
TEST_ANSWERS = {
    "firstName": "Jean",
    "lastName": "Dupont",
    "birthDate": "1990-05-15",
    "gender": "Male",
    "heightCm": 180,
    "weightKg": 75.5,
    "dietType": "omnivore",
    "activityLevel": "moderate",
}


async def test_onboarding():
    """Teste le flux complet d'onboarding."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # ============ 1️⃣ START - Créer la session ============
        print("\n🟢 [1] POST /onboarding/start")
        print(f"   user_id: {USER_ID}")
        
        resp = await client.post(
            f"{BASE_URL}/onboarding/start",
            params={"user_id": USER_ID}
        )
        
        if resp.status_code != 200:
            print(f"   ❌ Erreur {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        session_id = data["session_id"]
        first_question = data["question"]
        
        print(f"   ✅ Session créée: {session_id}")
        print(f"   📝 Première question: {first_question['text']}")
        print(f"      Slot: {first_question['slot']}")
        
        # ============ 2️⃣ ANSWER - Répondre aux 8 questions obligatoires ============
        print("\n🟢 [2] POST /onboarding/answer (8 questions obligatoires)")
        
        current_slot = first_question["slot"]
        question_count = 0
        
        for answer_key, answer_value in TEST_ANSWERS.items():
            question_count += 1
            
            print(f"\n   Q{question_count}: {current_slot}")
            print(f"   Réponse: {answer_value}")
            
            resp = await client.post(
                f"{BASE_URL}/onboarding/answer",
                json={
                    "session_id": session_id,
                    "slot": current_slot,
                    "value": answer_value
                }
            )
            
            if resp.status_code != 200:
                print(f"   ❌ Erreur {resp.status_code}: {resp.text}")
                return
            
            result = resp.json()
            
            # Vérifier si l'utilisateur a été créé (même si l'onboarding continue)
            if result.get("user_created"):
                print(f"   ✅ UTILISATEUR CRÉÉ!")
                print(f"   👤 User document ID: {result.get('user_document_id')}")
                print(f"   📋 Message: {result.get('message')}")
                
                if result.get("finished"):
                    print(f"   🏁 Onboarding complètement terminé!")
                    print(f"\n🎉 SUCCÈS - L'utilisateur a été créé en base de données!")
                    print(f"\nRésumé du profil créé:")
                    profile = result.get("profile_preview", {})
                    for k, v in profile.items():
                        print(f"   {k}: {v}")
                    return
                else:
                    print(f"   💬 Questions supplémentaires disponibles (optionnelles)")
                    print(f"\n🎉 SUCCÈS - L'utilisateur est créé, vous pouvez continuer avec les questions IA si vous voulez!")
                    return
            
            if result.get("finished"):
                print(f"   ✅ Onboarding terminé!")
                print(f"   👤 Utilisateur créé: {result.get('user_document_id')}")
                print(f"   📋 Message: {result.get('message')}")
                print("\n🎉 SUCCÈS - L'utilisateur a été créé en base de données!")
                print(f"\nRésumé du profil créé:")
                profile = result.get("profile_preview", {})
                for k, v in profile.items():
                    print(f"   {k}: {v}")
                return
            
            # Préparer la prochaine question
            next_q = result.get("next_question")
            if next_q:
                current_slot = next_q["slot"]
                print(f"   ✅ Réponse enregistrée")
                print(f"   📝 Prochaine question: {next_q['text']}")
                print(f"      Type: {next_q.get('type')}")
                if next_q.get("choices"):
                    print(f"      Choix: {next_q['choices']}")
            else:
                # Pas de prochaine question → onboarding terminé
                print(f"   ✅ Réponse enregistrée")
                print(f"   ⏳ En attente de la prochaine question...")


async def test_with_ai_questions():
    """
    Teste le flux avec les questions IA
    (si tu veux voir les questions proposées par l'IA)
    """
    print("\n" + "="*60)
    print("TEST AVEC QUESTIONS IA")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Démarrer
        resp = await client.post(
            f"{BASE_URL}/onboarding/start",
            params={"user_id": USER_ID + "_with_ai"}
        )
        data = resp.json()
        session_id = data["session_id"]
        
        print(f"\nSession: {session_id}")
        
        # Répondre aux 6 questions
        current_slot = data["question"]["slot"]
        
        for answer_key, answer_value in TEST_ANSWERS.items():
            resp = await client.post(
                f"{BASE_URL}/onboarding/answer",
                json={
                    "session_id": session_id,
                    "slot": current_slot,
                    "value": answer_value
                }
            )
            
            result = resp.json()
            
            if result.get("finished"):
                print(f"\n✅ Onboarding terminé (pas de questions IA)")
                return
            
            next_q = result.get("next_question")
            if next_q:
                current_slot = next_q["slot"]
                source = next_q.get("source", "manual")
                print(f"\n📝 Question ({source}): {next_q['text'][:80]}...")
        
        # À ce stade, on devrait avoir des questions IA
        print("\n💡 Les questions suivantes viendront de l'IA")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST ONBOARDING")
    print("="*60)
    print("\n⚠️  Assure-toi que ton serveur FastAPI est lancé!")
    print(f"   Base URL: {BASE_URL}")
    
    # Test 1 : Flux complet sans IA
    asyncio.run(test_onboarding())
    
    # Test 2 : Optionnel - avec questions IA
    # asyncio.run(test_with_ai_questions())