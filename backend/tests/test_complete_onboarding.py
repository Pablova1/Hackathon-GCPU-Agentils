"""
Test complet du nouveau flux d'onboarding avec 8 questions + réponses IA
"""
import asyncio
import httpx
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le dossier backend au path pour permettre les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.mongo_client import get_database

BASE_URL = "http://localhost:8000"
USER_ID = "test_complet_" + datetime.now().strftime("%Y%m%d_%H%M%S")

# Les 9 questions obligatoires
TEST_ANSWERS = {
    "firstName": "Sophie",
    "lastName": "Martin",
    "birthDate": "1992-08-20",
    "gender": "Female",
    "heightCm": 168,
    "weightKg": 62.0,
    "bodyType": "mesomorphic",
    "dietType": "vegetarian",
    "activityLevel": "high",
}

async def test_complete_flow():
    """Teste le flux complet avec questions obligatoires + IA."""
    
    # Timeout augmenté à 120s pour MongoDB Atlas (première connexion peut être lente)
    async with httpx.AsyncClient(timeout=120.0) as client:
        
        print(f"\n{'='*70}")
        print(f"TEST COMPLET - ONBOARDING AVEC 9 QUESTIONS + IA")
        print(f"{'='*70}")
        print(f"\n👤 User ID: {USER_ID}")
        
        # 1. Démarrer l'onboarding
        print(f"\n[1/3] 🚀 Démarrage de l'onboarding...")
        resp = await client.post(f"{BASE_URL}/onboarding/start", params={"user_id": USER_ID})
        
        if resp.status_code != 200:
            print(f"❌ Erreur: {resp.status_code} - {resp.text}")
            return
        
        data = resp.json()
        session_id = data["session_id"]
        current_slot = data["question"]["slot"]
        
        print(f"✅ Session créée: {session_id}")
        print(f"📝 Première question: {data['question']['text']}")
        
        # 2. Répondre aux questions obligatoires
        print(f"\n[2/3] 📋 Réponse aux {len(TEST_ANSWERS)} questions obligatoires...")
        
        question_num = 0
        for answer_key, answer_value in TEST_ANSWERS.items():
            question_num += 1
            
            print(f"\n   Q{question_num}/{len(TEST_ANSWERS)}: {current_slot}")
            print(f"   └─ Réponse: {answer_value}")
            
            resp = await client.post(
                f"{BASE_URL}/onboarding/answer",
                json={"session_id": session_id, "slot": current_slot, "value": answer_value}
            )
            
            if resp.status_code != 200:
                print(f"   ❌ Erreur: {resp.status_code} - {resp.text}")
                return
            
            result = resp.json()
            
            # Vérifier si l'utilisateur a été créé
            if result.get("user_created"):
                print(f"\n   🎉 UTILISATEUR CRÉÉ!")
                print(f"   └─ Document ID: {result.get('user_document_id')}")
                
                # Continuer avec les questions IA si disponibles
                if result.get("next_question"):
                    print(f"\n   💡 Question IA suggérée:")
                    print(f"   └─ {result['next_question']['text'][:100]}...")
                    current_slot = result["next_question"]["slot"]
                    
                    # Répondre à la question IA (exemple)
                    ai_answer = "Je fais du yoga 3 fois par semaine et j'adore les smoothies verts"
                    print(f"\n   🤖 Réponse à la question IA:")
                    print(f"   └─ {ai_answer}")
                    
                    resp = await client.post(
                        f"{BASE_URL}/onboarding/answer",
                        json={"session_id": session_id, "slot": current_slot, "value": ai_answer}
                    )
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        print(f"   ✅ Réponse IA enregistrée")
                        
                        if result.get("finished"):
                            print(f"   ✅ Onboarding terminé!")
                        elif result.get("next_question"):
                            print(f"   💡 Autre question IA disponible...")
                
                break
            
            # Prochaine question
            next_q = result.get("next_question")
            if next_q:
                current_slot = next_q["slot"]
                print(f"   ✅ Réponse enregistrée")
        
        # 3. Vérifier dans MongoDB
        print(f"\n[3/3] 🔍 Vérification dans MongoDB...")
        db = await get_database()
        user_collection = db["user"]
        
        user = await user_collection.find_one({"user_id": USER_ID})
        
        if user:
            print(f"\n✅ SUCCÈS - Utilisateur trouvé dans la collection 'user'!")
            print(f"\n📊 Détails du profil créé:")
            print(f"   └─ Prénom: {user.get('profile', {}).get('firstName')}")
            print(f"   └─ Nom: {user.get('profile', {}).get('lastName')}")
            print(f"   └─ Genre: {user.get('profile', {}).get('gender')}")
            print(f"   └─ Âge: {user.get('profile', {}).get('age')} ans")
            print(f"   └─ Taille: {user.get('profile', {}).get('height')} cm")
            print(f"   └─ Poids: {user.get('profile', {}).get('weight')} kg")
            print(f"   └─ Régime: {user.get('nutrition', {}).get('diet')}")
            print(f"   └─ Activité: {user.get('misc', {}).get('activityLevel')}")
            
            # Vérifier les réponses IA dans notes
            notes = user.get('misc', {}).get('notes')
            if notes:
                print(f"\n💬 Réponses IA (stockées dans misc.notes):")
                print(f"   └─ {notes}")
            else:
                print(f"\n💬 Aucune réponse IA enregistrée")
            
            print(f"\n   _id MongoDB: {user.get('_id')}")
            print(f"   Créé le: {user.get('createdAt')}")
        else:
            print(f"\n❌ ERREUR - Utilisateur non trouvé!")
        
        # Stats
        count_users = await user_collection.count_documents({})
        count_sessions = await db["onboarding_sessions"].count_documents({})
        print(f"\n📈 Statistiques:")
        print(f"   └─ Total utilisateurs: {count_users}")
        print(f"   └─ Total sessions: {count_sessions}")

if __name__ == "__main__":
    print("\n⚠️  Assurez-vous que le serveur FastAPI tourne sur http://localhost:8000\n")
    asyncio.run(test_complete_flow())
