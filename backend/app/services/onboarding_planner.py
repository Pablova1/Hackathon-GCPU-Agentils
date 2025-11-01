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

# Complete question bank for full onboarding form (29 questions in English)
FULL_QUESTION_BANK = {
    # Basic Information
    "birthDate": {
        "text": "What is your date of birth?",
        "type": "date",
        "required": True,
        "placeholder": "DD/MM/YYYY"
    },
    "gender": {
        "text": "What is your gender?",
        "type": "single_choice",
        "choices": ["Male", "Female", "Other"],
        "required": True
    },
    "heightCm": {
        "text": "What is your height (in cm)?",
        "type": "number",
        "required": True,
        "placeholder": "e.g., 175"
    },
    "weightKg": {
        "text": "What is your weight (in kg)?",
        "type": "number",
        "required": True,
        "placeholder": "e.g., 70"
    },
    "bodyType": {
        "text": "What is your body type?",
        "type": "single_choice",
        "choices": ["ectomorphic", "mesomorphic", "endomorphic", "unknown"],
        "required": True
    },
    
    # Nutrition
    "dietType": {
        "text": "Do you follow a specific diet?",
        "type": "single_choice",
        "choices": ["omnivore", "vegetarian", "vegan", "halal", "kosher", "other"],
        "required": True
    },
    "allergies": {
        "text": "Do you have any food allergies?",
        "type": "text",
        "required": False,
        "placeholder": "e.g., nuts, shellfish, dairy..."
    },
    "intolerances": {
        "text": "Do you have any food intolerances?",
        "type": "text",
        "required": False,
        "placeholder": "e.g., lactose, gluten..."
    },
    "foodLikes": {
        "text": "What foods do you particularly enjoy?",
        "type": "text",
        "required": False,
        "placeholder": "List your favorite foods..."
    },
    "foodDislikes": {
        "text": "What foods do you dislike or avoid?",
        "type": "text",
        "required": False,
        "placeholder": "Foods you prefer to avoid..."
    },
    "foodPreferences": {
        "text": "Any other food preferences or notes?",
        "type": "text",
        "required": False,
        "placeholder": "Any additional dietary preferences..."
    },
    
    # Health
    "treatments": {
        "text": "Are you currently taking any medications or treatments?",
        "type": "text",
        "required": False,
        "placeholder": "List any medications..."
    },
    "medicalHistoryPersonal": {
        "text": "Do you have any personal medical history we should know about?",
        "type": "text",
        "required": False,
        "placeholder": "Chronic conditions, past surgeries, etc..."
    },
    "medicalHistoryFamily": {
        "text": "Any relevant family medical history?",
        "type": "text",
        "required": False,
        "placeholder": "Diabetes, heart disease, etc..."
    },
    "birthControl": {
        "text": "Are you using birth control?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "birthControlName": {
        "text": "What type of birth control?",
        "type": "text",
        "required": False,
        "placeholder": "Name or type of birth control..."
    },
    
    # Goals
    "goalMuscleGain": {
        "text": "Is muscle gain one of your goals?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "goalWeightLoss": {
        "text": "Is weight loss one of your goals?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "goalPerformance": {
        "text": "Are you focused on athletic performance?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "goalMaintainShape": {
        "text": "Do you want to maintain your current shape?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "goalDetail": {
        "text": "Please describe your main health or fitness goals",
        "type": "text",
        "required": False,
        "placeholder": "What do you want to achieve?"
    },
    
    # Religious Restrictions
    "religiousPracticing": {
        "text": "Do you practice any religion with dietary restrictions?",
        "type": "single_choice",
        "choices": ["yes", "no"],
        "required": False
    },
    "religiousType": {
        "text": "Which religion or belief system?",
        "type": "text",
        "required": False,
        "placeholder": "e.g., Islam, Judaism, Hinduism..."
    },
    
    # Activity & Lifestyle
    "activityLevel": {
        "text": "What is your typical activity level?",
        "type": "single_choice",
        "choices": ["low", "moderate", "high"],
        "required": True
    },
    "sports": {
        "text": "What sports or physical activities do you do?",
        "type": "text",
        "required": False,
        "placeholder": "Running, yoga, swimming, etc..."
    },
    "occupation": {
        "text": "What is your occupation?",
        "type": "text",
        "required": False,
        "placeholder": "Your job or main activity..."
    },
    "additionalNotes": {
        "text": "Any additional information you'd like to share?",
        "type": "text",
        "required": False,
        "placeholder": "Anything else we should know..."
    }
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
