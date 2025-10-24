"""
Script d'inspection de la collection 'user'
Affiche tous les documents et leur structure pour comprendre comment elle est organisée.
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import json
from datetime import datetime
from app.db.mongo_client import get_database


def format_value(value):
    """Formate une valeur pour l'affichage."""
    if value is None:
        return "❌ None"
    elif isinstance(value, datetime):
        return f"📅 {value.strftime('%Y-%m-%d %H:%M:%S')}"
    elif isinstance(value, dict):
        return f"📦 Dict ({len(value)} clés)"
    elif isinstance(value, list):
        return f"📋 List ({len(value)} items)"
    elif isinstance(value, str):
        if len(value) > 50:
            return f"📝 '{value[:50]}...'"
        return f"📝 '{value}'"
    elif isinstance(value, bool):
        return "✅ True" if value else "❌ False"
    else:
        return f"🔢 {value}"


async def inspect_user_collection():
    """Inspecte la collection 'user' en détail."""
    print("=" * 80)
    print("  INSPECTION DE LA COLLECTION 'user'")
    print("=" * 80)
    
    db = await get_database()
    user_collection = db["user"]
    
    # Compter les documents
    total_count = await user_collection.count_documents({})
    print(f"\n📊 Total de documents: {total_count}")
    
    # Analyser les différents types de documents
    with_auth = await user_collection.count_documents({"email": {"$ne": None}})
    with_profile = await user_collection.count_documents({"profile": {"$exists": True}})
    with_medical = await user_collection.count_documents({"medical": {"$exists": True}})
    with_nutrition = await user_collection.count_documents({"nutrition": {"$exists": True}})
    
    print(f"\n📈 Statistiques:")
    print(f"   - Avec email (authentifiés): {with_auth}")
    print(f"   - Avec profil: {with_profile}")
    print(f"   - Avec infos médicales: {with_medical}")
    print(f"   - Avec infos nutrition: {with_nutrition}")
    
    # Lister tous les champs uniques
    print(f"\n🔑 Tous les champs présents dans la collection:")
    all_fields = set()
    async for doc in user_collection.find():
        all_fields.update(doc.keys())
    
    for field in sorted(all_fields):
        count = await user_collection.count_documents({field: {"$exists": True}})
        print(f"   - {field}: présent dans {count}/{total_count} documents")
    
    # Afficher quelques exemples de documents
    print(f"\n" + "=" * 80)
    print("  EXEMPLES DE DOCUMENTS")
    print("=" * 80)
    
    # 1. Document avec authentification
    print(f"\n{'─' * 80}")
    print("1️⃣  UTILISATEUR AVEC AUTHENTIFICATION (si existe)")
    print("─" * 80)
    
    doc_with_auth = await user_collection.find_one({"email": {"$ne": None}})
    if doc_with_auth:
        print(f"\n📄 ID MongoDB: {doc_with_auth['_id']}")
        for key, value in sorted(doc_with_auth.items()):
            if key != '_id':
                print(f"   {key:20} = {format_value(value)}")
                
                # Si c'est un dict, afficher son contenu
                if isinstance(value, dict) and key in ['profile', 'medical', 'nutrition']:
                    for sub_key, sub_value in value.items():
                        print(f"      ↳ {sub_key:17} = {format_value(sub_value)}")
    else:
        print("   ❌ Aucun utilisateur authentifié trouvé")
    
    # 2. Document sans authentification (onboarding seulement)
    print(f"\n{'─' * 80}")
    print("2️⃣  UTILISATEUR SANS AUTHENTIFICATION (onboarding seulement)")
    print("─" * 80)
    
    doc_without_auth = await user_collection.find_one({
        "$or": [
            {"email": None},
            {"email": {"$exists": False}}
        ]
    })
    
    if doc_without_auth:
        print(f"\n📄 ID MongoDB: {doc_without_auth['_id']}")
        for key, value in sorted(doc_without_auth.items()):
            if key != '_id':
                print(f"   {key:20} = {format_value(value)}")
                
                # Si c'est un dict, afficher son contenu
                if isinstance(value, dict) and key in ['profile', 'medical', 'nutrition']:
                    for sub_key, sub_value in value.items():
                        print(f"      ↳ {sub_key:17} = {format_value(sub_value)}")
    else:
        print("   ❌ Aucun utilisateur sans auth trouvé")
    
    # 3. Tous les documents (résumé)
    print(f"\n{'─' * 80}")
    print("3️⃣  RÉSUMÉ DE TOUS LES DOCUMENTS")
    print("─" * 80)
    
    print(f"\n{'ID':24} | {'Email':30} | {'Username':15} | Profile | Medical | Nutrition")
    print("─" * 110)
    
    async for doc in user_collection.find().sort("_id", 1):
        doc_id = str(doc['_id'])[:22]
        email = doc.get('email', 'N/A')
        if email and len(email) > 28:
            email = email[:25] + "..."
        username = doc.get('username', 'N/A')
        if username and len(username) > 13:
            username = username[:10] + "..."
        
        has_profile = "✅" if doc.get('profile') else "❌"
        has_medical = "✅" if doc.get('medical') else "❌"
        has_nutrition = "✅" if doc.get('nutrition') else "❌"
        
        print(f"{doc_id:24} | {email or 'N/A':30} | {username or 'N/A':15} | {has_profile:7} | {has_medical:7} | {has_nutrition:9}")
    
    # Vérifier les index
    print(f"\n{'─' * 80}")
    print("4️⃣  INDEX ACTUELS")
    print("─" * 80)
    
    indexes = await user_collection.list_indexes().to_list(None)
    for idx in indexes:
        print(f"\n   📌 {idx['name']}")
        print(f"      Clés: {idx['key']}")
        if 'unique' in idx:
            print(f"      Unique: {idx['unique']}")
        if 'sparse' in idx:
            print(f"      Sparse: {idx['sparse']}")
    
    print(f"\n" + "=" * 80)
    print("  FIN DE L'INSPECTION")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(inspect_user_collection())
