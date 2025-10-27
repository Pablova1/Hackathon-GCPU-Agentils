REQUIRED_SLOTS = [
    # Informations de base
    "birthDate",
    "gender",
    "heightCm",
    "weightKg",
    "bodyType",
    
    # Nutrition
    "dietType",
    "foodLikes",
    
    # Santé
    "birthControl",
    
    # Objectifs
    "goalMuscleGain",
    "goalWeightLoss",
    "goalPerformance",
    "goalMaintainShape",
    "goalDetail",
    
    # Restrictions religieuses
    "religiousPracticing",
    
    # Activité et mode de vie
    "activityLevel",
    "occupation",
]

# Questions optionnelles (non requises)
OPTIONAL_SLOTS = [
    "allergies",
    "intolerances",
    "foodDislikes",
    "foodPreferences",
    "treatments",
    "medicalHistoryPersonal",
    "medicalHistoryFamily",
    "birthControlName",  # Conditionnelle : apparaît seulement si birthControl = "oui"
    "religiousType",  # Conditionnelle : apparaît seulement si religiousPracticing = "oui"
    "sports",
    "additionalNotes",
]

QUESTION_BANK = {
    # ===== INFORMATIONS DE BASE =====
    "birthDate": {
        "text": "What is your date of birth?", 
        "type": "date", 
        "placeholder": "DD/MM/YYYY"
    },
    "gender": {
        "text": "What is your gender?", 
        "type": "single_choice",
        "choices": ["Male", "Female", "Other"]
    },
    "heightCm": {
        "text": "What is your height (in cm)?", 
        "type": "number", 
        "placeholder": "Ex: 170"
    },
    "weightKg": {
        "text": "What is your weight (in kg)?", 
        "type": "number", 
        "placeholder": "Ex: 70"
    },
    "bodyType": {
        "text": "What is your body type?", 
        "type": "single_choice",
        "choices": ["ectomorphic", "mesomorphic", "endomorphic", "unknown"]
    },
    
    # ===== NUTRITION =====
    "dietType": {
        "text": "What is your diet type?", 
        "type": "single_choice",
        "choices": ["omnivore", "vegetarian", "vegan", "halal", "kosher", "other"]
    },
    "allergies": {
        "text": "Do you have any food allergies? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: peanuts, seafood"
    },
    "intolerances": {
        "text": "Do you have any food intolerances? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: lactose, gluten"
    },
    "foodLikes": {
        "text": "What foods do you particularly like? (separate by commas)", 
        "type": "text", 
        "placeholder": "Ex: pasta, chicken, green vegetables"
    },
    "foodDislikes": {
        "text": "What foods do you dislike? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: fish, spinach"
    },
    "foodPreferences": {
        "text": "General preferences (organic, local, etc.)? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: organic, local"
    },
    
    # ===== SANTÉ =====
    "treatments": {
        "text": "Are you taking any medical treatments? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: Levothyrox 75mcg"
    },
    "medicalHistoryPersonal": {
        "text": "Do you have any personal medical history? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: type 2 diabetes, hypertension"
    },
    "medicalHistoryFamily": {
        "text": "Do you have any family medical history? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: diabetes, heart disease"
    },
    "birthControl": {
        "text": "Are you using any form of birth control?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "birthControlName": {
        "text": "Which one?", 
        "type": "text", 
        "placeholder": "Ex: pill, IUD"
    },
    
    # ===== OBJECTIFS =====
    "goalMuscleGain": {
        "text": "Do you want to gain muscle?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "goalWeightLoss": {
        "text": "Do you want to lose weight?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "goalPerformance": {
        "text": "Do you want to improve your athletic performance?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "goalMaintainShape": {
        "text": "Do you want to maintain your current shape?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "goalDetail": {
        "text": "Describe your main goal in a few words", 
        "type": "text", 
        "placeholder": "Ex: Lose 5kg in 3 months, Build muscle mass"
    },
    
    # ===== RESTRICTIONS RELIGIEUSES =====
    "religiousPracticing": {
        "text": "Do you have any religious dietary restrictions?", 
        "type": "single_choice",
        "choices": ["yes", "no"]
    },
    "religiousType": {
        "text": "Which ones?", 
        "type": "text", 
        "placeholder": "Ex: halal, kosher"
    },
    
    # ===== ACTIVITÉ ET MODE DE VIE =====
    "activityLevel": {
        "text": "What is your physical activity level?", 
        "type": "single_choice",
        "choices": ["low", "moderate", "high"]
    },
    "sports": {
        "text": "What sports do you practice? (separate by commas, leave blank if none)", 
        "type": "text", 
        "placeholder": "Ex: running, yoga, weight training"
    },
    "occupation": {
        "text": "What is your main profession or occupation?", 
        "type": "text", 
        "placeholder": "Ex: student, engineer, sales"
    },
    "additionalNotes": {
        "text": "Is there any other important information we should know about you? (optional)", 
        "type": "text", 
        "placeholder": "Ex: Prefer to eat early in the evening, often eat out"
    },
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
    # Questions obligatoires
    for slot in REQUIRED_SLOTS:
        q = dict(QUESTION_BANK[slot])  # copie
        q["slot"] = slot
        q["required"] = True
        questions.append(q)
    # Questions optionnelles
    for slot in OPTIONAL_SLOTS:
        q = dict(QUESTION_BANK[slot])  # copie
        q["slot"] = slot
        q["required"] = False
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
