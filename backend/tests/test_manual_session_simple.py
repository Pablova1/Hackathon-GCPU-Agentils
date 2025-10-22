"""
Script de test manuel du système de sessions.
Permet de créer une session et d'analyser une image d'assiette.

Usage:
    python tests/test_manual_session_simple.py
    
    Ou pour analyser une image spécifique:
    python tests/test_manual_session_simple.py --image chemin/vers/image.jpg
"""

import requests
import json
import sys
from pathlib import Path
import argparse


API_BASE_URL = "http://localhost:8000/api"


def print_banner(text):
    """Affiche un bandeau coloré."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_server():
    """Vérifie que le serveur est accessible."""
    print("[1/5] Vérification du serveur...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Serveur actif\n")
            return True
    except requests.exceptions.RequestException:
        print("❌ Serveur non accessible. Démarrez-le avec: python run.py\n")
        return False


def create_session(user_id="test_manual_user"):
    """Crée une nouvelle session."""
    print("[2/5] Création d'une nouvelle session...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/session/create",
            json={"user_id": user_id},
            timeout=5
        )
        
        if response.status_code == 200:
            session_data = response.json()
            token = session_data["session_token"]
            user_id = session_data["user_id"]
            
            print("✅ Session créée avec succès!")
            print(f"   User ID:       {user_id}")
            print(f"   Session Token: {token}\n")
            
            return token, user_id
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}\n")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la création: {e}\n")
        return None, None


def validate_session(token):
    """Valide que la session est active."""
    print("[3/5] Validation de la session...")
    
    try:
        headers = {"X-Session-Token": token}
        response = requests.get(
            f"{API_BASE_URL}/session/info",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            info = response.json()
            print("✅ Session valide!")
            print(f"   Créée le:          {info['created_at']}")
            print(f"   Dernière activité: {info['last_activity']}\n")
            return True
        else:
            print(f"❌ Session invalide: {response.text}\n")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}\n")
        return False


def analyze_plate(token, image_path):
    """Analyse une image d'assiette."""
    print(f"[4/5] Analyse de l'image: {image_path}")
    
    if not Path(image_path).exists():
        print(f"❌ Fichier introuvable: {image_path}\n")
        return None
    
    try:
        headers = {"X-Session-Token": token}
        
        # Déterminer le type MIME
        import mimetypes
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'image/png'  # Par défaut
        
        with open(image_path, 'rb') as img_file:
            # Spécifier explicitement le type MIME
            files = {'file': (Path(image_path).name, img_file, mime_type)}
            response = requests.post(
                f"{API_BASE_URL}/analyze/plate",
                headers=headers,
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analyse réussie!")
            print(f"\n🍽️  {result['nombre_aliments']} aliment(s) détecté(s):\n")
            
            for i, aliment in enumerate(result['aliments'], 1):
                print(f"   {i}. {aliment['name']:<30} {aliment['estimated_quantity']:>4}g")
            
            print()
            return result
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}\n")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'analyse: {e}\n")
        return None


def get_history(token):
    """Récupère l'historique des analyses."""
    print("[5/5] Récupération de l'historique...")
    
    try:
        headers = {"X-Session-Token": token}
        response = requests.get(
            f"{API_BASE_URL}/analyze/history",
            headers=headers,
            params={"limit": 5},
            timeout=5
        )
        
        if response.status_code == 200:
            history = response.json()
            
            print(f"✅ {history['total']} analyse(s) dans l'historique\n")
            
            if history['total'] > 0:
                for i, analysis in enumerate(history['analyses'], 1):
                    print(f"   Analyse #{i} - {analysis['analyzed_at']}")
                    print(f"   → {analysis['nombre_aliments']} aliment(s) détecté(s)")
                    if i < len(history['analyses']):
                        print()
            
            print()
            return history
        else:
            print(f"⚠️  Erreur: {response.text}\n")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}\n")
        return None


def main():
    parser = argparse.ArgumentParser(description='Test manuel du système de sessions')
    parser.add_argument(
        '--image',
        default=r'C:\Users\valen\OneDrive\Bureau\ESILV_A5\Hackathon\image_assiette_0.png',
        help='Chemin vers l\'image à analyser'
    )
    parser.add_argument(
        '--user-id',
        default='test_manual_user',
        help='ID utilisateur pour la session'
    )
    
    args = parser.parse_args()
    
    print_banner("🔐 Test Manuel du Système de Sessions")
    
    # 1. Vérifier le serveur
    if not check_server():
        sys.exit(1)
    
    # 2. Créer une session
    token, user_id = create_session(args.user_id)
    if not token:
        sys.exit(1)
    
    # 3. Valider la session
    if not validate_session(token):
        sys.exit(1)
    
    # 4. Analyser une image
    result = analyze_plate(token, args.image)
    
    # 5. Récupérer l'historique
    history = get_history(token)
    
    # Résumé final
    print_banner("✨ Résumé")
    print(f"🔑 Token de session: {token}")
    print(f"👤 User ID:          {user_id}")
    print(f"\n📝 Votre session est active et prête à être utilisée!")
    print(f"\nPour réutiliser ce token dans d'autres requêtes:")
    print(f"   export SESSION_TOKEN={token}")
    print(f"\nOu dans PowerShell:")
    print(f"   $env:SESSION_TOKEN='{token}'")
    print(f"\nExemple de commande:")
    print(f'   curl.exe -X GET "http://localhost:8000/api/analyze/history" \\')
    print(f'            -H "X-Session-Token: {token}"')
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
