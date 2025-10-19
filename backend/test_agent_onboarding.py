"""
Test direct de l'agent onboarding pour diagnostiquer les problèmes
"""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

# Charger le .env
env_path = Path(__file__).parent.parent / ".env"
print(f"📁 Chargement du .env depuis: {env_path}")
print(f"✅ Fichier existe: {env_path.exists()}\n")
load_dotenv(dotenv_path=env_path, override=True)

# Vérifier les variables
print("🔑 Variables d'environnement:")
api_key = os.getenv('GOOGLE_API_KEY')
project_id = os.getenv('GCP_PROJECT_ID')
region = os.getenv('GCP_REGION')

print(f"  GOOGLE_API_KEY: {api_key[:20] + '...' if api_key else 'MANQUANT'}")
print(f"  GCP_PROJECT_ID: {project_id or 'MANQUANT'}")
print(f"  GCP_REGION: {region or 'MANQUANT'}\n")

# Importer et initialiser l'agent
try:
    from app.ai.agents.agent_onboarding import OnboardingAgent
    
    print("🤖 Initialisation de l'agent...")
    agent = OnboardingAgent()
    print(f"✅ Agent initialisé avec succès!")
    print(f"  Project ID: {agent.project_id}")
    print(f"  Region: {agent.region}\n")
    
    # Tester avec un contexte utilisateur
    print("📋 Test de génération de question...")
    slots = {
        "firstName": "Sophie",
        "lastName": "Martin",
        "birthDate": "1992-08-20",
        "gender": "Female",
        "heightCm": 168,
        "weightKg": 62.0,
        "bodyType": "mesomorphic",
        "dietType": "vegetarian",
        "activityLevel": "high"
    }
    
    question = agent.suggest_followup(slots, asked_ai_count=0)
    
    if question:
        print(f"✅ Question générée avec succès!")
        print(f"  Slot: {question['slot']}")
        print(f"  Question: {question['text']}\n")
    else:
        print(f"❌ Aucune question générée (retour None)\n")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
