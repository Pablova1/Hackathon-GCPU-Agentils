"""Test de l'analyse d'image avec le nouvel agent."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
import os

# Charger les variables d'environnement
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

print(f"API_KEY: {os.getenv('API_KEY', 'MANQUANT')[:30]}...")
print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY', 'MANQUANT')[:30]}...")

try:
    from app.ai.agents.agent_assiette_0.agent import FoodAnalyzerAgent
    
    print("\n🔄 Initialisation de l'agent...")
    agent = FoodAnalyzerAgent()
    print(f"✅ Agent initialisé")
    
    # Test avec une image de test (créons une image simple pour le test)
    print("\n📝 Création d'une image de test...")
    from PIL import Image
    import io
    
    # Créer une petite image de test
    img = Image.new('RGB', (100, 100), color='red')
    test_image_path = Path(__file__).parent / "test_plate.jpg"
    img.save(test_image_path)
    print(f"✅ Image créée: {test_image_path}")
    
    print("\n🔍 Test de l'analyse...")
    result = agent.analyze_plate(str(test_image_path))
    print(f"✅ Analyse réussie!")
    print(f"Résultat: {result}")
    
    # Nettoyer
    test_image_path.unlink()
    print("\n✅ Tous les tests réussis!")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
