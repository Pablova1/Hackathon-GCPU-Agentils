# Architecture du Système de Sessions

## Flux d'utilisation

```
┌─────────────┐
│   CLIENT    │
│  (Frontend) │
└──────┬──────┘
       │
       │ 1. POST /api/session/create
       │    { "user_id": "alice" }
       ▼
┌─────────────────────┐
│   API BACKEND       │
│  SessionManager     │
└──────┬──────────────┘
       │
       │ 2. Crée session dans MongoDB
       │    + génère session_token
       ▼
┌─────────────────────┐
│     MongoDB         │
│  user_sessions      │
│  ├─ session_token   │
│  ├─ user_id         │
│  ├─ created_at      │
│  ├─ expires_at      │
│  └─ metadata        │
└──────┬──────────────┘
       │
       │ 3. Retourne session_token
       ▼
┌─────────────┐
│   CLIENT    │
│  Stocke:    │
│  session_   │
│  token      │
└──────┬──────┘
       │
       │ 4. Requêtes suivantes avec
       │    Header: X-Session-Token
       ▼
┌─────────────────────┐
│   API BACKEND       │
│  get_current_       │
│  session()          │
│                     │
│  ✓ Vérifie validité │
│  ✓ Met à jour       │
│    last_activity    │
│  ✓ Retourne user_id │
└──────┬──────────────┘
       │
       │ 5. Sauvegarde l'analyse
       ▼
┌─────────────────────┐
│     MongoDB         │
│  plate_analyses     │
│  ├─ user_id         │
│  ├─ session_token   │
│  ├─ aliments        │
│  └─ analyzed_at     │
└─────────────────────┘
```

## Collections MongoDB

### 1. user_sessions
```
{
  "_id": ObjectId("..."),
  "session_token": "abc-123-def-456",
  "user_id": "alice_123",
  "created_at": ISODate("2025-10-20T10:00:00"),
  "last_activity": ISODate("2025-10-20T15:30:00"),
  "expires_at": ISODate("2025-10-21T10:00:00"),
  "metadata": {
    "onboarding_completed": true,
    "total_analyses": 5,
    "total_requests": 12
  }
}
```

### 2. plate_analyses
```
{
  "_id": ObjectId("..."),
  "user_id": "alice_123",
  "session_token": "abc-123-def-456",
  "image_filename": "uuid-here.jpg",
  "aliments": [
    {"name": "Poulet", "estimated_quantity": 150},
    {"name": "Riz", "estimated_quantity": 200}
  ],
  "nombre_aliments": 2,
  "analyzed_at": "2025-10-20T15:30:00"
}
```

### 3. nutrient_analyses
```
{
  "_id": ObjectId("..."),
  "user_id": "alice_123",
  "session_token": "abc-123-def-456",
  "aliments": [...],
  "nutrients": {...},
  "nutrient_summary": {
    "total_calories": 450,
    "total_protein": 35,
    ...
  },
  "analyzed_at": "2025-10-20T15:35:00"
}
```

## Middleware FastAPI

```python
# Dans analyze.py
@router.post("/plate")
async def analyze_plate(
    file: UploadFile = File(...),
    session: dict = Depends(get_current_session)  # ← Injection automatique
):
    user_id = session["user_id"]  # ← Récupération de l'utilisateur
    # ...
    # Sauvegarde liée à user_id
```

## Avantages du système

✅ **Tracking automatique** : Toutes les actions sont liées à un utilisateur
✅ **Sécurité** : Vérification automatique de la validité de la session
✅ **Historique** : Possibilité de consulter toutes les analyses passées
✅ **Statistiques** : Suivi du nombre d'analyses, d'activité, etc.
✅ **Multi-sessions** : Un utilisateur peut avoir plusieurs sessions actives
✅ **Expiration** : Les sessions expirent automatiquement après 24h

## Comparaison Avant/Après

### AVANT (sans sessions)
```
❌ Pas d'identification utilisateur sur /analyze/plate
❌ Impossible de savoir qui a analysé quoi
❌ Pas d'historique
❌ user_id passé manuellement (non sécurisé)
```

### APRÈS (avec sessions)
```
✅ Chaque requête est liée à un utilisateur authentifié
✅ Historique complet des analyses par utilisateur
✅ Statistiques d'utilisation
✅ session_token sécurisé avec expiration
✅ Middleware FastAPI pour validation automatique
```
