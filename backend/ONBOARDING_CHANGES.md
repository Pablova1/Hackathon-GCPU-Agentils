# 📋 Récapitulatif des Modifications - Onboarding

## ✅ Changements Effectués

### 1. Questions Obligatoires Enrichies (8 questions au lieu de 6)

**Fichier**: `app/services/onboarding_planner.py`

Les questions obligatoires ont été étendues pour couvrir tous les champs essentiels du `ProfileCore`:

```python
REQUIRED_SLOTS = [
    "firstName",      # Nouveau ✨
    "lastName",       # Nouveau ✨
    "birthDate",
    "gender",         # Nouveau ✨
    "heightCm",
    "weightKg",
    "dietType",
    "activityLevel",
]
```

**Nouvelles questions ajoutées**:
- ✨ **lastName**: "Quel est ton nom de famille ?"
- ✨ **gender**: "Quel est ton genre ?" (choix: Male, Female, Other)

**ActivityLevel ajusté** pour correspondre au modèle:
- Anciens choix: sedentary, light, moderate, active, very_active
- Nouveaux choix: **low, moderate, high** (conforme à `ActivityLevel` du modèle)

---

### 2. Stockage des Réponses IA dans "Divers"

**Fichier**: `app/api/onboarding.py`

La fonction `map_minimal_slots_to_full_profile()` a été mise à jour pour:

1. **Séparer** les réponses obligatoires des réponses IA
2. **Stocker** les réponses IA dans `misc.notes`

```python
# Extraire les réponses IA (slots qui commencent par "ai_followup_")
ai_responses = {}
regular_slots = {}

for key, value in slots.items():
    if key.startswith("ai_followup_"):
        ai_responses[key] = value  # Réponses IA
    else:
        regular_slots[key] = value  # Réponses obligatoires

# Créer une note avec les réponses IA
notes = None
if ai_responses:
    notes_list = [f"{key}: {value}" for key, value in ai_responses.items()]
    notes = "Informations supplémentaires - " + " | ".join(notes_list)
```

**Résultat**: Les réponses aux questions IA sont stockées dans le champ `misc.notes` du document utilisateur.

---

### 3. Changement de Collection MongoDB

**Fichier**: `app/db/user_store.py`

Tous les utilisateurs sont maintenant créés dans la collection **`user`** (singulier) au lieu de `users` (pluriel):

```python
users_collection = db["user"]  # Collection 'user' au singulier
```

**Dans MongoDB Compass**:
- Base de données: `feel_good`
- Collection: **`user`** ← Regardez ici !

---

## 📊 Structure du Document Utilisateur

```json
{
  "_id": "ObjectId(...)",
  "user_id": "test_user_20251017_123456",
  "profile": {
    "firstName": "Sophie",
    "lastName": "Martin",
    "age": 33,
    "gender": "Female",
    "weight": 62.0,
    "height": 168.0,
    "bodyType": "unknown"
  },
  "medical": {
    "treatments": [],
    "allergies": [],
    "medicalHistory": { "personal": [], "family": [] },
    "birthControl": null
  },
  "nutrition": {
    "diet": "vegetarian",
    "intolerances": [],
    "preferences": { "liked": [], "disliked": [], "general": [] }
  },
  "goals": {
    "muscleGain": false,
    "weightLoss": false,
    "goalDetail": null,
    "performance": false,
    "maintainShape": false
  },
  "religiousRestrictions": null,
  "misc": {
    "activityLevel": "high",
    "sports": [],
    "occupation": null,
    "notes": "Informations supplémentaires - ai_followup_0: Je fais du yoga 3 fois par semaine"
  },
  "createdAt": "2025-10-17T14:30:00.000Z"
}
```

---

## 🧪 Tests Disponibles

### Test Simple (8 questions obligatoires uniquement)
```bash
cd C:\Users\ASUS\Desktop\Hackathon-GCPU-Agentils\backend\tests
python test_onboarding.py
```

### Test Complet (8 questions + réponses IA)
```bash
cd C:\Users\ASUS\Desktop\Hackathon-GCPU-Agentils\backend
python test_complete_onboarding.py
```

### Vérifier la base de données
```bash
cd C:\Users\ASUS\Desktop\Hackathon-GCPU-Agentils\backend
python show_db_info.py
```

---

## 🎯 Flux d'Onboarding Mis à Jour

1. **START** → Création de la session
2. **8 questions obligatoires** → Réponses enregistrées dans `slots`
3. **Création de l'utilisateur** → Dès que les 8 questions sont répondues
4. **Questions IA (optionnelles)** → Maximum 3 questions supplémentaires
5. **Stockage des réponses IA** → Dans `misc.notes`
6. **FIN** → Session marquée comme COMPLETED

---

## ✨ Avantages

1. ✅ **Profil plus complet** dès le départ (nom, genre, etc.)
2. ✅ **Cohérence** avec le modèle `UserDocument`
3. ✅ **Séparation claire** entre données obligatoires et informations supplémentaires
4. ✅ **Traçabilité** des réponses IA dans le champ `notes`
5. ✅ **Collection unique** `user` pour tous les utilisateurs

---

## 🔄 Prochaines Étapes Possibles

- [ ] Ajouter plus de questions obligatoires (objectifs, allergies, etc.)
- [ ] Améliorer le parsing des réponses IA pour remplir automatiquement d'autres champs
- [ ] Créer un endpoint pour mettre à jour le profil après onboarding
- [ ] Ajouter une validation plus stricte des réponses
