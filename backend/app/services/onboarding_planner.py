REQUIRED_SLOTS = [
    # Informations de base
    "birthDate",
    "gender",
    "heightCm",
    "weightKg",
    "bodyType",
    
    # Nutrition
    "dietType",
    "allergies",
    "intolerances",
    "foodLikes",
    "foodDislikes",
    "foodPreferences",
    
    # Santé
    "treatments",
    "medicalHistoryPersonal",
    "medicalHistoryFamily",
    "birthControl",
    "birthControlName",
    
    # Objectifs
    "goalMuscleGain",
    "goalWeightLoss",
    "goalPerformance",
    "goalMaintainShape",
    "goalDetail",
    
    # Restrictions religieuses
    "religiousPracticing",
    "religiousType",
    
    # Activité et mode de vie
    "activityLevel",
    "sports",
    "occupation",
    "additionalNotes",
]

QUESTION_BANK = {
    # ===== INFORMATIONS DE BASE =====
    "birthDate": {
        "text": "Quelle est ta date de naissance ?", 
        "type": "date", 
        "placeholder": "JJ/MM/AAAA"
    },
    "gender": {
        "text": "Quel est ton genre ?", 
        "type": "single_choice",
        "choices": ["Male", "Female", "Other"]
    },
    "heightCm": {
        "text": "Quelle est ta taille (en cm) ?", 
        "type": "number", 
        "placeholder": "Ex: 170"
    },
    "weightKg": {
        "text": "Quel est ton poids (en kg) ?", 
        "type": "number", 
        "placeholder": "Ex: 70"
    },
    "bodyType": {
        "text": "Quel est ton type de morphologie ?", 
        "type": "single_choice",
        "choices": ["ectomorphic", "mesomorphic", "endomorphic", "unknown"]
    },
    
    # ===== NUTRITION =====
    "dietType": {
        "text": "Quel est ton régime alimentaire ?", 
        "type": "single_choice",
        "choices": ["omnivore", "vegetarian", "vegan", "halal", "kosher", "autre"]
    },
    "allergies": {
        "text": "As-tu des allergies alimentaires ? (sépare par des virgules, ou écris 'aucune')", 
        "type": "text", 
        "placeholder": "Ex: arachides, fruits de mer, aucune"
    },
    "intolerances": {
        "text": "As-tu des intolérances alimentaires ? (sépare par des virgules, ou écris 'aucune')", 
        "type": "text", 
        "placeholder": "Ex: lactose, gluten, aucune"
    },
    "foodLikes": {
        "text": "Quels aliments aimes-tu particulièrement ? (sépare par des virgules)", 
        "type": "text", 
        "placeholder": "Ex: pâtes, poulet, légumes verts"
    },
    "foodDislikes": {
        "text": "Quels aliments n'aimes-tu pas ? (sépare par des virgules, ou écris 'aucun')", 
        "type": "text", 
        "placeholder": "Ex: poisson, épinards, aucun"
    },
    "foodPreferences": {
        "text": "Préférences générales (bio, local, etc.) ? (sépare par des virgules, ou écris 'aucune')", 
        "type": "text", 
        "placeholder": "Ex: bio, local, aucune"
    },
    
    # ===== SANTÉ =====
    "treatments": {
        "text": "Prends-tu des traitements médicaux ? (sépare par des virgules, ou écris 'aucun')", 
        "type": "text", 
        "placeholder": "Ex: Levothyrox 75mcg, aucun"
    },
    "medicalHistoryPersonal": {
        "text": "As-tu des antécédents médicaux personnels ? (sépare par des virgules, ou écris 'aucun')", 
        "type": "text", 
        "placeholder": "Ex: diabète type 2, hypertension, aucun"
    },
    "medicalHistoryFamily": {
        "text": "As-tu des antécédents médicaux familiaux ? (sépare par des virgules, ou écris 'aucun')", 
        "type": "text", 
        "placeholder": "Ex: diabète, maladies cardiaques, aucun"
    },
    "birthControl": {
        "text": "Utilises-tu un moyen de contraception ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "birthControlName": {
        "text": "Si oui, lequel ? (sinon écris 'non applicable')", 
        "type": "text", 
        "placeholder": "Ex: pilule, stérilet, non applicable"
    },
    
    # ===== OBJECTIFS =====
    "goalMuscleGain": {
        "text": "Souhaites-tu prendre du muscle ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "goalWeightLoss": {
        "text": "Souhaites-tu perdre du poids ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "goalPerformance": {
        "text": "Souhaites-tu améliorer tes performances sportives ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "goalMaintainShape": {
        "text": "Souhaites-tu maintenir ta forme actuelle ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "goalDetail": {
        "text": "Décris ton objectif principal en quelques mots", 
        "type": "text", 
        "placeholder": "Ex: Perdre 5kg en 3 mois, Prendre de la masse musculaire"
    },
    
    # ===== RESTRICTIONS RELIGIEUSES =====
    "religiousPracticing": {
        "text": "As-tu des restrictions alimentaires religieuses ?", 
        "type": "single_choice",
        "choices": ["oui", "non"]
    },
    "religiousType": {
        "text": "Si oui, lesquelles ? (sinon écris 'non applicable')", 
        "type": "text", 
        "placeholder": "Ex: halal, casher, non applicable"
    },
    
    # ===== ACTIVITÉ ET MODE DE VIE =====
    "activityLevel": {
        "text": "Quel est ton niveau d'activité physique ?", 
        "type": "single_choice",
        "choices": ["low", "moderate", "high"]
    },
    "sports": {
        "text": "Quels sports pratiques-tu ? (sépare par des virgules, ou écris 'aucun')", 
        "type": "text", 
        "placeholder": "Ex: course à pied, yoga, musculation, aucun"
    },
    "occupation": {
        "text": "Quelle est ta profession ou occupation principale ?", 
        "type": "text", 
        "placeholder": "Ex: étudiant, ingénieur, commercial"
    },
    "additionalNotes": {
        "text": "Y a-t-il d'autres informations importantes à savoir sur toi ? (optionnel)", 
        "type": "text", 
        "placeholder": "Ex: Préfère manger tôt le soir, mange souvent au restaurant"
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
