REQUIRED_SLOTS = [
    # "firstName" et "lastName" supprimés car déjà fournis lors de l'inscription
    "birthDate",
    "gender",
    "heightCm",
    "weightKg",
    "bodyType",
    "dietType",
    "activityLevel",
]

QUESTION_BANK = {
    # Questions nom/prénom retirées car déjà dans l'inscription
    "birthDate":    {"text": "Quelle est ta date de naissance ?", "type": "date", "placeholder": "JJ/MM/AAAA"},
    "gender":       {"text": "Quel est ton genre ?", "type": "single_choice",
                     "choices": ["Male", "Female", "Other"]},
    "heightCm":     {"text": "Quelle est ta taille (en cm) ?", "type": "number", "placeholder": "Ex: 170"},
    "weightKg":     {"text": "Quel est ton poids (en kg) ?", "type": "number", "placeholder": "Ex: 70"},
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

def all_questions() -> list[dict]:
    """Retourne toutes les questions requises pour l'onboarding."""
    questions = []
    for slot in REQUIRED_SLOTS:
        q = dict(QUESTION_BANK[slot])  # copie
        q["slot"] = slot
        q["required"] = True
        questions.append(q)
    return questions

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
