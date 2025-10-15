# Slots requis (MVP)
REQUIRED_SLOTS = [
    "first_name",
    "birth_date",
    "height_cm",
    "weight_kg",
    "diet_type",
    "activity_level",
]

# Banque de questions minimaliste
QUESTION_BANK = {
    "first_name":     {"text": "Quel est ton prénom ?", "type": "text"},
    "birth_date":     {"text": "Quelle est ta date de naissance ? (YYYY-MM-DD)", "type": "text"},
    "height_cm":      {"text": "Quelle est ta taille (en cm) ?", "type": "number"},
    "weight_kg":      {"text": "Quel est ton poids (en kg) ?", "type": "number"},
    "diet_type":      {"text": "As-tu un régime alimentaire particulier ?", "type": "single_choice",
                       "choices": ["omnivore","vegetarian","vegan","halal","kosher","autre"]},
    "activity_level": {"text": "Quel est ton niveau d’activité ?", "type": "single_choice",
                       "choices": ["sedentary","light","moderate","active","very_active"]},
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
