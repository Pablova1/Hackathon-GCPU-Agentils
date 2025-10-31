REQUIRED_SLOTS = [
    "firstName",
    "lastName",
    "birthDate",
    "gender",
    "heightCm",
    "weightKg",
    "bodyType",
    "dietType",
    "activityLevel",
]

QUESTION_BANK = {
    "firstName":    {"text": "Quel est ton prénom ?", "type": "text"},
    "lastName":     {"text": "Quel est ton nom de famille ?", "type": "text"},
    "birthDate":    {"text": "Quelle est ta date de naissance ? (YYYY-MM-DD)", "type": "text"},
    "gender":       {"text": "Quel est ton genre ?", "type": "single_choice",
                     "choices": ["Male", "Female", "Other"]},
    "heightCm":     {"text": "Quelle est ta taille (en cm) ?", "type": "number"},
    "weightKg":     {"text": "Quel est ton poids (en kg) ?", "type": "number"},
    "bodyType":     {"text": "Quel est ton type de morphologie ?", "type": "single_choice",
                     "choices": ["ectomorphic", "mesomorphic", "endomorphic", "unknown"]},
    "dietType":     {"text": "As-tu un régime alimentaire particulier ?", "type": "single_choice",
                     "choices": ["omnivore","vegetarian","vegan","halal","kosher","autre"]},
    "activityLevel": {"text": "Quel est ton niveau d'activité physique ?", "type": "single_choice",
                      "choices": ["low","moderate","high"]},
}

def first_question() -> dict:
    """Retourne la première question (le 1er slot requis)."""
    slot = REQUIRED_SLOTS[0]
    q = dict(QUESTION_BANK[slot])  # copie
    q["slot"] = slot
    return q

def next_required_slot(slots: dict) -> str | None:
    """Renvoie le prochain slot requis manquant, ou None si tout est rempli."""
    for s in REQUIRED_SLOTS:
        if s not in slots:
            return s
    return None

def question_for_slot(slot: str) -> dict:
    """Construit l'objet question pour un slot donné."""
    q = dict(QUESTION_BANK[slot])  # copie
    q["slot"] = slot
    return q
