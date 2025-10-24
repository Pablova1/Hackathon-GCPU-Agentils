# 🎯 RÉORGANISATION DU SCHÉMA UTILISATEUR - 20 octobre 2025

## ✅ CHANGEMENTS EFFECTUÉS

### 1. Structure du document modifiée

**AVANT:**
```json
{
  "user_id": "user_abc123",
  "email": "user@example.com",           ← À la racine
  "username": "alice_martin",            ← À la racine (SUPPRIMÉ)
  "password_hash": "...",
  "profile": {
    "firstName": "Alice",
    "lastName": "Martin",
    "age": 28,
    ...
  }
}
```

**APRÈS:**
```json
{
  "user_id": "user_abc123",
  "password_hash": "...",
  "profile": {
    "firstName": "Alice",
    "lastName": "Martin",
    "email": "user@example.com",         ← Déplacé dans profile
    "age": 28,
    "gender": "Female",
    "weight": 62.0,
    "height": 168.0,
    "bodyType": "mesomorphic"
  },
  "medical": { ... },
  "nutrition": { ... },
  "goals": { ... },
  "religiousRestrictions": { ... },
  "misc": { ... }
}
```

---

## 📊 ÉTAT FINAL

### Collection `user`

**5 utilisateurs:**

| Prénom | Nom | Email | Profil |
|--------|-----|-------|--------|
| Sophie | Durand | tes@hotmail.com | ✅ Complet |
| Sophie | Durand | sophie.durand@test-hackathon.com | ✅ Complet |
| TestPrenom | TestNom | testprenom.testnom@test-hackathon.com | ✅ Complet |
| Sophie | Martin | sophie.martin@test-hackathon.com | ✅ Complet |
| (Valou) | (Valou) | valentin.rech@osehf.srjo | ⚠️  Profil vide |

**Note:** L'utilisateur Valou n'a pas de profil, donc son email reste temporairement à la racine pour compatibilité.

---

## 🔑 INDEX MONGODB

### Avant
```python
- _id_
- email_1 (unique, sparse)          ← Sur email à la racine
- username_1 (unique, sparse)       ← SUPPRIMÉ
- user_id_1 (unique, sparse)
```

### Après
```python
- _id_
- profile.email_1 (unique, sparse)  ← Nouveau
- user_id_1 (unique, sparse)
```

---

## 🔄 FICHIERS MODIFIÉS

### 1. Modèle

**`backend/app/models/profile_model.py`**
```python
class ProfileCore(BaseModel):
    """Informations de profil de base."""
    firstName: str
    lastName: str
    email: str  # ← Ajouté
    age: int
    gender: Gender
    weight: float
    height: float
    bodyType: Optional[BodyType]

class UserDocument(BaseModel):
    user_id: str
    password_hash: str
    # Suppression de 'email' et 'username' à la racine
    profile: Optional[ProfileCore]
    medical: Optional[Medical]
    ...
```

### 2. Routes d'authentification

**`backend/app/api/routes/auth.py`** (complètement refait)

**Inscription (AVANT):**
```json
POST /api/auth/register
{
    "email": "user@example.com",
    "password": "pass123",
    "username": "alice"  ← Supprimé
}
```

**Inscription (APRÈS):**
```json
POST /api/auth/register
{
    "email": "user@example.com",
    "password": "pass123",
    "first_name": "Alice",  ← Nouveau
    "last_name": "Martin"   ← Nouveau
}
```

**Réponse:**
```json
{
    "success": true,
    "session_token": "...",
    "user_id": "user_abc123",
    "email": "user@example.com",
    "first_name": "Alice",  ← Au lieu de username
    "last_name": "Martin"   ← Au lieu de username
}
```

---

## 📝 MIGRATIONS EXÉCUTÉES

### 1. Réorganisation du schéma
**Script:** `migrations/reorganize_schema.py`
- ✅ Déplacé `email` → `profile.email` pour 4 utilisateurs
- ✅ Supprimé `username` pour 5 utilisateurs

### 2. Mise à jour des index
**Script:** `migrations/update_indexes.py`
- ✅ Supprimé index `username_1`
- ✅ Supprimé index `email_1` (racine)
- ✅ Créé index `profile.email_1` (unique, sparse)

---

## 🚀 UTILISATION

### Inscription

```bash
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
    "email": "alice.martin@example.com",
    "password": "SecurePass123",
    "first_name": "Alice",
    "last_name": "Martin"
}

# Réponse
{
    "success": true,
    "message": "Compte créé avec succès",
    "session_token": "abc123...",
    "user_id": "user_def456",
    "email": "alice.martin@example.com",
    "first_name": "Alice",
    "last_name": "Martin"
}
```

### Connexion

```bash
POST http://localhost:8000/api/auth/login
Content-Type: application/json

{
    "email": "alice.martin@example.com",
    "password": "SecurePass123"
}

# Réponse
{
    "success": true,
    "message": "Connexion réussie",
    "session_token": "ghi789...",
    "user_id": "user_def456",
    "email": "alice.martin@example.com",
    "first_name": "Alice",
    "last_name": "Martin"
}
```

---

## 🔒 PROTECTION

### Index de protection
```python
# Empêche les doublons d'email
db.user.create_index("profile.email", unique=True, sparse=True)

# Empêche les doublons d'user_id
db.user.create_index("user_id", unique=True, sparse=True)
```

**Résultat:**
- ❌ Impossible de créer deux utilisateurs avec le même `profile.email`
- ❌ Impossible de créer deux utilisateurs avec le même `user_id`
- ✅ Les documents sans profil (email=null) sont autorisés (sparse=True)

---

## ⚙️ COMPATIBILITÉ ARRIÈRE

Le système de connexion supporte les deux formats pour une transition en douceur :

```python
# Chercher l'utilisateur par email
user = await users.find_one({
    "$or": [
        {"profile.email": request.email.lower()},  # Nouveau format
        {"email": request.email.lower()}           # Ancien format (fallback)
    ]
})
```

**Impact:**
- ✅ Les anciens utilisateurs (email à la racine) peuvent toujours se connecter
- ✅ Les nouveaux utilisateurs (email dans profile) fonctionnent normalement
- ✅ Migration progressive sans coupure de service

---

## 📋 SCHÉMA FINAL COMPLET

```json
{
  "_id": ObjectId("..."),
  "user_id": "user_abc123",
  "password_hash": "sha256...",
  "created_at": "2025-10-20T14:00:00Z",
  "last_login": "2025-10-20T15:00:00Z",
  "profile_completed": true,
  
  "profile": {
    "firstName": "Alice",
    "lastName": "Martin",
    "email": "alice.martin@example.com",
    "age": 28,
    "gender": "Female",
    "weight": 62.0,
    "height": 168.0,
    "bodyType": "mesomorphic"
  },
  
  "medical": {
    "treatments": [],
    "allergies": ["peanuts"],
    "medicalHistory": {
      "personal": [],
      "family": []
    },
    "birthControl": null
  },
  
  "nutrition": {
    "diet": "vegetarian",
    "intolerances": ["lactose"],
    "preferences": {
      "liked": ["pasta", "salad"],
      "disliked": ["mushrooms"],
      "general": []
    }
  },
  
  "goals": {
    "muscleGain": false,
    "weightLoss": true,
    "goalDetail": "Lose 5kg",
    "performance": false,
    "maintainShape": false
  },
  
  "religiousRestrictions": null,
  
  "misc": {
    "activityLevel": "moderate",
    "sports": ["running", "yoga"],
    "occupation": "Software Engineer",
    "notes": null
  }
}
```

---

## ✅ CHECKLIST

- [x] Email déplacé dans `profile.email`
- [x] Champ `username` supprimé
- [x] Index `username_1` supprimé
- [x] Index `email_1` supprimé
- [x] Index `profile.email_1` créé
- [x] Routes d'authentification mises à jour
- [x] Modèle `ProfileCore` mis à jour
- [x] Compatibilité arrière maintenue
- [x] Tests de connexion réussis

---

## 🎉 RÉSULTAT

**Le schéma est maintenant plus logique et cohérent !**

✅ **Avantages:**
- Email logiquement groupé avec prénom/nom dans `profile`
- Pas de redondance (`username` supprimé)
- Structure plus claire et intuitive
- Index plus pertinents

✅ **Structure cohérente:**
```
{
  user_id + password_hash   ← Authentification
  profile {                 ← Identité complète
    firstName, lastName, email, age, gender, ...
  }
  medical { ... }           ← Santé
  nutrition { ... }         ← Nutrition
  goals { ... }             ← Objectifs
  ...
}
```

**Date:** 20 octobre 2025  
**Statut:** ✅ **COMPLET ET TESTÉ**
