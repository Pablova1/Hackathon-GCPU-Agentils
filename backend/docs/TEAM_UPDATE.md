# 📢 Pour l'équipe : Changements du Schéma Utilisateur

Salut l'équipe ! 👋

J'ai fait une refonte du schéma utilisateur pour le rendre cohérent et éviter les bugs. Voici ce qui a changé :

---

## 🎯 Problème résolu

**Avant** : On avait 2 collections qui se marchaient dessus :
- `users` (pluriel) pour l'authentification
- `user` (singulier) pour le profil

Résultat : Des données dupliquées, des bugs, et de la confusion.

**Maintenant** : **UNE SEULE collection** `user` (singulier) pour tout.

---

## ✅ Ce qui change pour vous

### 1. Nom de collection

```python
# ❌ AVANT (ne plus faire)
db["users"]

# ✅ MAINTENANT (toujours faire)
db["user"]
```

### 2. Structure du document

Un utilisateur = Un seul document avec **tout dedans** :

```json
{
  "user_id": "user_abc123",
  
  // Auth (créé à l'inscription)
  "email": "alice@example.com",
  "username": "Alice",
  "password_hash": "...",
  "profile_completed": false,
  
  // Profil (ajouté à l'onboarding)
  "profile": {...},  // null jusqu'à l'onboarding
  "medical": {...},
  "nutrition": {...}
}
```

### 3. Workflow

```
Inscription → Crée dans 'user' avec profil=null
    ↓
Onboarding → Met à jour le MÊME document avec le profil
    ↓
Un seul document complet ✅
```

---

## 🔧 Fichiers modifiés

| Fichier | Quoi | Action requise |
|---------|------|----------------|
| `models/profile_model.py` | Ajout champs d'auth | ✅ Rien, c'est fait |
| `api/routes/auth.py` | `users` → `user` | ✅ Rien, c'est fait |
| `db/user_store.py` | Insert → Update | ✅ Rien, c'est fait |

---

## 💡 Ce qui ne change PAS

- Les endpoints API sont **identiques**
- Le frontend ne change **pas**
- Les sessions fonctionnent **pareil**
- L'onboarding fonctionne **pareil** (juste en interne c'est mieux)

---

## 🧪 Comment tester

### Test rapide (30 secondes)

```bash
cd backend
python tests/test_unified_schema.py
```

Vérifie que :
- ✅ La collection `user` existe
- ✅ Pas de collection `users` (pluriel)
- ✅ Le schéma est correct

### Test complet (2 minutes)

```bash
# 1. Vérifier la BDD
python tests/test_database_consistency.py

# 2. Tester l'auth
python tests/test_auth_api.py

# 3. Tester l'onboarding
python tests/test_complete_onboarding.py
```

---

## ⚠️ Si vous avez du code qui touche aux users

### À vérifier

```python
# ✅ Remplacer ça :
db["users"]

# ✅ Par ça :
db["user"]
```

### Exemple de code à modifier

```python
# ❌ AVANT
users_collection = db["users"]
user = await users_collection.find_one({"email": email})

# ✅ MAINTENANT
users_collection = db["user"]  # Singulier !
user = await users_collection.find_one({"email": email})
```

---

## 📚 Documentation

J'ai créé 3 docs complètes (si vous voulez en savoir plus) :

1. **`docs/USER_SCHEMA.md`** - Schéma complet avec exemples
2. **`docs/SCHEMA_MIGRATION.md`** - Historique des changements
3. **`docs/UNIFORMISATION_COMPLETE.md`** - Résumé technique

---

## 🆘 Besoin d'aide ?

### J'ai une erreur dans mes tests

→ Vérifie que tu utilises `db["user"]` et pas `db["users"]`

### Ma fonction d'onboarding ne marche plus

→ Normal, elle a été corrigée pour faire une mise à jour au lieu d'une insertion.  
→ Regarde `db/user_store.py` pour voir le nouveau code.

### J'ai des données dans l'ancienne collection `users`

→ Voir le script de migration dans `docs/SCHEMA_MIGRATION.md`

---

## 🎉 Avantages

✅ **Plus clair** : 1 collection = 1 source de vérité  
✅ **Plus sûr** : Pas de risque de données dupliquées  
✅ **Plus cohérent** : Même schéma partout  
✅ **Plus facile** : Les champs d'auth sont protégés automatiquement  

---

## 🚀 Backend démarré

Le backend tourne déjà avec ces changements :

```
✅ http://localhost:8000
✅ Docs: http://localhost:8000/docs
```

Vous pouvez tester directement ! 🎯

---

**Questions ?** Demandez-moi ou lisez la doc complète dans `docs/` 📖

Bon code ! 💪
