"""Test de l'agent onboarding pour comparer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import os

# Charger les variables d'environnement
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print(f"API_KEY: {os.getenv('API_KEY', 'MANQUANT')[:30]}...")

try:
    from app.ai.agents.agent_onboarding.agent import OnboardingAgent
    
    print("\n🔄 Initialisation de l'agent onboarding...")
    agent = OnboardingAgent()
    print(f"✅ Agent initialisé")
    
    print("\n🔍 Test de génération de question...")
    slots = {
        "age": 25,
        "gender": "homme",
        "weight": 75,
        "height": 180
    }
    result = agent.suggest_followup(slots, 0)
    print(f"✅ Question générée: {result}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
