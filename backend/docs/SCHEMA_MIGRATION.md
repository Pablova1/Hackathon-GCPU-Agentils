# 🔄 Uniformisation du Schéma Utilisateur

## 📅 Date : 20 octobre 2025

## 🎯 Objectif

Uniformiser la gestion des utilisateurs pour avoir **une seule collection MongoDB** avec un schéma cohérent entre l'authentification et le profil nutritionnel.

---

## ⚠️ Changements importants

### 1. Nom de collection

| Avant | Après |
|-------|-------|
| `users` (pluriel) | `user` (singulier) |
| Collections séparées auth/profil | Collection unique |

### 2. Structure du document

**Avant** (incohérent) :
- Collection `users` : Juste l'auth
- Collection `user` : Juste le profil

**Après** (unifié) :
- Collection `user` : Auth + Profil dans le même document

---

## 📊 Nouveau schéma

```json
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123",
  
  // Auth (créé à l'inscription)
  "email": "alice@example.com",
  "username": "Alice",
  "password_hash": "sha256...",
  "created_at": ISODate("..."),
  "last_login": ISODate("..."),
  "profile_completed": false,
  
  // Profil (ajouté à l'onboarding)
  "profile": {...},      // null jusqu'à l'onboarding
  "medical": {...},      // null jusqu'à l'onboarding
  "nutrition": {...},    // null jusqu'à l'onboarding
  "goals": {...},        // null jusqu'à l'onboarding
  "religiousRestrictions": {...},
  "misc": {...}
}
```

---

## 🔧 Fichiers modifiés

### 1. `app/models/profile_model.py`

**Modification** : Ajout des champs d'authentification au modèle `UserDocument`

```python
class UserDocument(BaseModel):
    # ✅ NOUVEAU: Champs d'authentification
    user_id: str
    email: str
    username: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    profile_completed: bool = False
    
    # ✅ MODIFIÉ: Profil devient optionnel
    profile: Optional[ProfileCore] = None
    medical: Optional[Medical] = None
    nutrition: Optional[Nutrition] = None
    goals: Optional[Goals] = None
    # ...
```

### 2. `app/api/routes/auth.py`

**Modifications** :
- ✅ Changé `db["users"]` → `db["user"]` partout
- ✅ Ajout des champs de profil à `null` lors de l'inscription

```python
@router.post("/register")
async def register(request: RegisterRequest):
    users = db["user"]  # ← Singulier maintenant
    
    user_data = {
        "user_id": f"user_{secrets.token_hex(8)}",
        "email": request.email.lower(),
        "username": request.username,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now(),
        "profile_completed": False,
        # ✅ NOUVEAU: Initialiser les champs de profil à null
        "profile": None,
        "medical": None,
        "nutrition": None,
        "goals": None,
        "religiousRestrictions": None,
        "misc": None
    }
    
    await users.insert_one(user_data)
```

### 3. `app/db/user_store.py`

**Modification** : `create_user_document()` devient une **mise à jour** au lieu d'une insertion

**Avant** :
```python
async def create_user_document(user_id: str, slots: dict) -> dict:
    # Créait un NOUVEAU document
    await users_collection.insert_one(doc_dict)
```

**Après** :
```python
async def create_user_document(user_id: str, slots: dict) -> dict:
    # Vérifie que l'utilisateur existe
    existing_user = await users_collection.find_one({"user_id": user_id})
    if not existing_user:
        raise ValueError("Inscription requise avant l'onboarding")
    
    # Met à jour SEULEMENT les champs de profil
    profile_updates = {
        "profile": profile.model_dump(),
        "medical": medical.model_dump(),
        # ... SANS toucher à email, username, password_hash
    }
    
    result = await users_collection.find_one_and_update(
        {"user_id": user_id},
        {"$set": profile_updates},
        return_document=True
    )
```

---

## 🔄 Workflow mis à jour

### Avant (problématique)

```
1. Inscription → Crée dans 'users'
2. Onboarding → Crée dans 'user'
❌ Résultat: 2 documents séparés
```

### Après (correct)

```
1. Inscription → Crée dans 'user' avec auth + profil=null
2. Onboarding → Met à jour le même document avec le profil
✅ Résultat: 1 document complet
```

---

## 📝 Documentation créée

1. **`docs/USER_SCHEMA.md`**  
   Documentation complète du schéma utilisateur

2. **`tests/test_database_consistency.py`**  
   Script de vérification de la cohérence de la BDD

3. **Ce fichier (`SCHEMA_MIGRATION.md`)**  
   Historique des changements

---

## 🧪 Comment tester

### 1. Vérifier la cohérence de la base

```bash
cd backend
python tests/test_database_consistency.py
```

**Ce script vérifie** :
- ✅ Que la collection `user` existe
- ✅ Qu'il n'y a pas de collection `users` (pluriel)
- ✅ La structure des documents
- ✅ Les index
- ✅ Les statistiques

### 2. Tester l'inscription

```bash
python tests/test_auth_api.py
```

**Vérifie** :
- ✅ Inscription crée bien dans `user`
- ✅ Les champs de profil sont à `null`
- ✅ `profile_completed = false`

### 3. Tester l'onboarding

```bash
python tests/test_complete_onboarding.py
```

**Vérifie** :
- ✅ L'onboarding met à jour le document existant
- ✅ Les champs d'auth ne sont pas modifiés
- ✅ `profile_completed = true` après onboarding

---

## 🔑 Index recommandés

```javascript
// À exécuter dans MongoDB Shell ou via le script de test

db.user.createIndex({ "email": 1 }, { unique: true })
db.user.createIndex({ "username": 1 }, { unique: true })
db.user.createIndex({ "user_id": 1 }, { unique: true })
db.user.createIndex({ "profile_completed": 1 })
```

---

## ⚠️ Points d'attention

### ❌ Ne JAMAIS faire

```python
# ❌ Utiliser "users" (pluriel)
db["users"]

# ❌ Créer un nouveau document à l'onboarding
await users.insert_one(...)  # L'utilisateur existe déjà!

# ❌ Écraser les champs d'auth
await users.update_one(
    {"user_id": user_id},
    {"$set": {
        "email": "...",         # DANGEREUX
        "password_hash": "..."  # DANGEREUX
    }}
)
```

### ✅ Toujours faire

```python
# ✅ Utiliser "user" (singulier)
db["user"]

# ✅ Mettre à jour à l'onboarding
await users.find_one_and_update(...)

# ✅ Protéger les champs d'auth
profile_updates = {
    "profile": {...},
    "medical": {...},
    # PAS email, username, password_hash
}
```

---

## 🗄️ Migration d'anciennes données

Si vous avez déjà des données dans `users` (pluriel), voici comment migrer :

```python
# Script de migration (à adapter selon vos besoins)
async def migrate_users():
    db = await get_database()
    
    # Copier tous les documents de 'users' vers 'user'
    old_users = db["users"]
    new_users = db["user"]
    
    async for doc in old_users.find():
        # Ajouter les champs de profil à null
        doc["profile"] = None
        doc["medical"] = None
        doc["nutrition"] = None
        doc["goals"] = None
        
        # Insérer dans la nouvelle collection
        await new_users.insert_one(doc)
    
    print(f"Migration terminée !")
    
    # OPTIONNEL: Supprimer l'ancienne collection
    # await db.drop_collection("users")
```

---

## 📚 Références

- [USER_SCHEMA.md](USER_SCHEMA.md) - Schéma complet
- [AUTH_README.md](../AUTH_README.md) - Documentation de l'authentification
- [SESSIONS_README.md](SESSIONS_README.md) - Gestion des sessions

---

## ✅ Checklist de vérification

Après cette migration, vérifiez :

- [ ] La collection s'appelle bien `user` (singulier)
- [ ] Tous les fichiers utilisent `db["user"]`
- [ ] L'inscription crée les champs de profil à `null`
- [ ] L'onboarding met à jour (ne crée pas) le document
- [ ] Les index sont créés sur `email`, `username`, `user_id`
- [ ] Les tests passent
- [ ] La documentation est à jour

---

**Date de mise en œuvre** : 20 octobre 2025  
**Auteur** : GitHub Copilot + Équipe Agentils  
**Version** : 1.0
