# 📋 Schéma Utilisateur - Collection `user`

## 🎯 Vue d'ensemble

La collection MongoDB **`user`** (singulier) contient **TOUS** les utilisateurs avec leurs informations d'authentification ET leur profil nutritionnel.

### Changements importants

✅ **Collection unique** : `user` (pas `users` au pluriel)  
✅ **Schéma unifié** : Authentification + Profil dans le même document  
✅ **Workflow** : Inscription → Onboarding → Profil complet

---

## 📊 Structure du document

```json
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123def456",
  
  // ─────────────────────────────────────────
  // AUTHENTIFICATION (créé à l'inscription)
  // ─────────────────────────────────────────
  "email": "alice@example.com",
  "username": "Alice",
  "password_hash": "sha256_hash_here",
  "created_at": ISODate("2025-10-20T10:30:00Z"),
  "last_login": ISODate("2025-10-20T14:25:00Z"),
  "profile_completed": false,  // true après onboarding
  
  // ─────────────────────────────────────────
  // PROFIL NUTRITIONNEL (ajouté après onboarding)
  // ─────────────────────────────────────────
  "profile": {
    "lastName": "Dupont",
    "firstName": "Alice",
    "age": 28,
    "gender": "Female",
    "weight": 65.0,
    "height": 168.0,
    "bodyType": "mesomorphic"
  },
  
  "medical": {
    "treatments": [
      {
        "name": "Levothyrox",
        "dosage": "75mcg",
        "condition": "Hypothyroïdie"
      }
    ],
    "allergies": ["arachides", "lactose"],
    "medicalHistory": {
      "personal": ["diabète type 2"],
      "family": ["hypertension"]
    },
    "birthControl": {
      "uses": true,
      "name": "Pilule"
    }
  },
  
  "nutrition": {
    "diet": "végétarien",
    "intolerances": ["gluten", "lactose"],
    "preferences": {
      "liked": ["pâtes", "légumes verts", "fruits"],
      "disliked": ["poisson", "épinards"],
      "general": ["bio", "local"]
    }
  },
  
  "goals": {
    "muscleGain": false,
    "weightLoss": true,
    "goalDetail": "Perdre 5kg en 3 mois",
    "performance": false,
    "maintainShape": false
  },
  
  "religiousRestrictions": {
    "practicing": true,
    "type": "halal"
  },
  
  "misc": {
    "activityLevel": "moderate",
    "sports": ["course à pied", "yoga"],
    "occupation": "ingénieure",
    "notes": "Préfère manger tôt le soir"
  },
  
  "createdAt": ISODate("2025-10-20T10:35:00Z")
}
```

---

## 🔄 Workflow complet

### 1️⃣ Inscription (Auth)

**Endpoint** : `POST /api/auth/register`

```json
{
  "email": "alice@example.com",
  "password": "monMotDePasse123",
  "username": "Alice"
}
```

**MongoDB** : Crée un document dans `user` avec :
- ✅ `user_id` généré
- ✅ `email`, `username`, `password_hash`
- ✅ `created_at`, `last_login`
- ✅ `profile_completed: false`
- ❌ `profile`, `medical`, etc. → `null`

**Réponse** :
```json
{
  "success": true,
  "message": "Inscription réussie !",
  "session_token": "abc-123-def-456",
  "user_id": "user_abc123",
  "username": "Alice",
  "email": "alice@example.com"
}
```

---

### 2️⃣ Onboarding (Profil)

**Endpoint** : `POST /api/onboarding/complete/{user_id}`

```json
{
  "lastName": "Dupont",
  "firstName": "Alice",
  "age": 28,
  "gender": "Female",
  "weight_kg": 65.0,
  "height_cm": 168.0,
  "bodyType": "mesomorphic",
  "diet": "végétarien",
  "allergies": ["arachides", "lactose"],
  "muscleGain": false,
  "weightLoss": true,
  "goalDetail": "Perdre 5kg",
  "activityLevel": "moderate",
  "sports": ["course à pied", "yoga"]
}
```

**MongoDB** : Met à jour le document existant avec :
- ✅ Ajoute `profile`, `medical`, `nutrition`, `goals`, etc.
- ✅ Met `profile_completed: true`
- ❌ NE touche PAS à `email`, `username`, `password_hash`

---

### 3️⃣ Connexion

**Endpoint** : `POST /api/auth/login`

```json
{
  "email": "alice@example.com",
  "password": "monMotDePasse123"
}
```

**MongoDB** : 
1. Cherche l'utilisateur par `email`
2. Vérifie le `password_hash`
3. Met à jour `last_login`
4. Crée une session

---

## 🛠️ Fonctions principales

### `auth.py`

```python
# Inscription - crée l'utilisateur avec auth uniquement
@router.post("/register")
async def register(request: RegisterRequest):
    users = db["user"]  # ← Collection 'user' (singulier)
    
    user_data = {
        "user_id": f"user_{secrets.token_hex(8)}",
        "email": request.email.lower(),
        "username": request.username,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now(),
        "profile_completed": False,
        "profile": None,  # ← Sera rempli à l'onboarding
        "medical": None,
        "nutrition": None,
        # ...
    }
    await users.insert_one(user_data)
```

### `user_store.py`

```python
# Onboarding - met à jour le profil de l'utilisateur existant
async def create_user_document(user_id: str, slots: dict) -> dict:
    users = db["user"]  # ← Même collection
    
    # Vérifier que l'utilisateur existe
    existing_user = await users.find_one({"user_id": user_id})
    if not existing_user:
        raise ValueError("Inscription requise avant l'onboarding")
    
    # Construire le profil
    profile = ProfileCore(...)
    medical = Medical(...)
    # ...
    
    # Mettre à jour SEULEMENT les champs de profil
    profile_updates = {
        "profile": profile.model_dump(),
        "medical": medical.model_dump(),
        "nutrition": nutrition.model_dump(),
        "goals": goals.model_dump(),
        "profile_completed": True,
        # NE PAS toucher à email, username, password_hash
    }
    
    result = await users.find_one_and_update(
        {"user_id": user_id},
        {"$set": profile_updates},
        return_document=True
    )
```

---

## 🔍 Requêtes MongoDB utiles

### Voir tous les utilisateurs

```javascript
db.user.find({})
```

### Voir les utilisateurs avec profil complet

```javascript
db.user.find({ profile_completed: true })
```

### Voir les utilisateurs sans profil

```javascript
db.user.find({ profile_completed: false })
```

### Chercher par email

```javascript
db.user.findOne({ email: "alice@example.com" })
```

### Compter par statut

```javascript
db.user.aggregate([
  {
    $group: {
      _id: "$profile_completed",
      count: { $sum: 1 }
    }
  }
])
```

---

## ⚠️ Points d'attention

### ❌ Ne JAMAIS faire

```python
# ❌ Utiliser la collection "users" (pluriel)
db["users"]  # FAUX

# ❌ Écraser les champs d'auth pendant l'onboarding
update = {
  "email": "nouveau@email.com",  # DANGEREUX
  "password_hash": "...",         # DANGEREUX
  # ...
}
```

### ✅ Toujours faire

```python
# ✅ Utiliser la collection "user" (singulier)
db["user"]  # CORRECT

# ✅ Mettre à jour uniquement les champs de profil
profile_updates = {
  "profile": {...},
  "medical": {...},
  "nutrition": {...},
  # PAS email, username, password_hash
}
await users.update_one(
  {"user_id": user_id},
  {"$set": profile_updates}
)
```

---

## 📚 Modèle Pydantic

Le modèle `UserDocument` dans `profile_model.py` a été mis à jour :

```python
class UserDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    
    # Authentification (requis à l'inscription)
    email: str
    username: str
    password_hash: str
    
    # Profil (optionnel jusqu'à l'onboarding)
    profile: Optional[ProfileCore] = None
    medical: Optional[Medical] = None
    nutrition: Optional[Nutrition] = None
    goals: Optional[Goals] = None
    religiousRestrictions: Optional[ReligiousRestrictions] = None
    misc: Optional[Misc] = None
    
    # Métadonnées
    created_at: datetime
    last_login: Optional[datetime] = None
    profile_completed: bool = False
```

---

## 🧪 Tests

### Tester l'inscription

```bash
cd backend
python tests/test_auth_api.py
```

### Tester l'onboarding

```bash
python tests/test_complete_onboarding.py
```

### Vérifier la collection dans MongoDB

```bash
python tests/test_user_collection.py
```

---

## 📖 Voir aussi

- [AUTH_README.md](../AUTH_README.md) - Documentation de l'authentification
- [SESSIONS_README.md](../docs/SESSIONS_README.md) - Gestion des sessions
- [QUICK_START_SESSIONS.md](../docs/QUICK_START_SESSIONS.md) - Guide rapide
