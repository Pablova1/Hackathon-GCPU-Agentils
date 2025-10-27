"""Test d'initialisation des agents."""
import os
import sys
from pathlib import Path

# Ajouter le dossier backend au path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Charger les variables d'environnement
env_path = Path(__file__).parent.parent / ".env"
print(f"Chargement du .env depuis: {env_path}")
load_dotenv(dotenv_path=env_path)

# Afficher les variables d'environnement
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY', 'MANQUANT')[:30]}...")
print(f"API_KEY: {os.getenv('API_KEY', 'MANQUANT')[:30]}...")

# Tester l'import des agents
try:
    print("\n1. Test import FoodAnalyzerAgent...")
    from app.ai.agents.agent_assiette_0.agent import FoodAnalyzerAgent
    print("   ✅ Import réussi")
    
    print("\n2. Test initialisation FoodAnalyzerAgent...")
    food_agent = FoodAnalyzerAgent()
    print(f"   ✅ Agent initialisé avec le modèle: {food_agent.model_name}")
    
    print("\n3. Test import NutrientAnalyzerAgent...")
    from app.ai.agents.agent_assiette_1.agent import NutrientAnalyzerAgent
    print("   ✅ Import réussi")
    
    print("\n4. Test initialisation NutrientAnalyzerAgent...")
    nutrient_agent = NutrientAnalyzerAgent()
    print(f"   ✅ Agent initialisé avec le modèle: {nutrient_agent.model_name}")
    
    print("\n✅ Tous les tests ont réussi!")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
