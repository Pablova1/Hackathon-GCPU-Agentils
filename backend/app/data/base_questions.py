base_questions = [

    # ---------------------- PROFIL ----------------------
    {
        "id": "firstName",
        "text": "Quel est votre prénom ?",
        "type": "text",
        "category": "Profil"
    },
    {
        "id": "lastName",
        "text": "Quel est votre nom de famille ?",
        "type": "text",
        "category": "Profil"
    },
    {
        "id": "age",
        "text": "Quel est votre âge ?",
        "type": "number",
        "category": "Profil"
    },
    {
        "id": "gender",
        "text": "Quel est votre genre ?",
        "type": "choice",
        "choices": ["Femme", "Homme", "Autre"],
        "category": "Profil"
    },
    {
        "id": "height",
        "text": "Quelle est votre taille (en cm) ?",
        "type": "number",
        "category": "Profil"
    },
    {
        "id": "weight",
        "text": "Quel est votre poids (en kg) ?",
        "type": "number",
        "category": "Profil"
    },
    {
        "id": "bodyType",
        "text": "Connaissez-vous votre morphologie ?",
        "type": "choice",
        "choices": ["Ectomorphe", "Mésomorphe", "Endomorphe", "Je ne sais pas"],
        "category": "Profil"
    },

    # ---------------------- MÉDICAL ----------------------
    {
        "id": "treatments",
        "text": "Suivez-vous actuellement un traitement médical ? Si oui, lequel ?",
        "type": "text",
        "category": "Médical"
    },
    {
        "id": "allergies",
        "text": "Avez-vous des allergies connues ?",
        "type": "text",
        "category": "Médical"
    },
    {
        "id": "medicalHistory",
        "text": "Avez-vous des antécédents médicaux personnels ou familiaux importants ?",
        "type": "text",
        "category": "Médical"
    },
    {
        "id": "birthControl",
        "text": "Utilisez-vous une contraception hormonale (pilule, implant, etc.) ?",
        "type": "choice",
        "choices": ["Oui", "Non"],
        "category": "Médical"
    },

    # ---------------------- NUTRITION ----------------------
    {
        "id": "diet",
        "text": "Suivez-vous un régime alimentaire particulier ?",
        "type": "choice",
        "choices": ["Aucun", "Végétarien", "Végétalien", "Sans gluten", "Autre"],
        "category": "Nutrition"
    },
    {
        "id": "intolerances",
        "text": "Avez-vous des intolérances ou restrictions alimentaires ?",
        "type": "text",
        "category": "Nutrition"
    },
    {
        "id": "preferences.liked",
        "text": "Quels aliments aimez-vous particulièrement ?",
        "type": "text",
        "category": "Nutrition"
    },
    {
        "id": "preferences.disliked",
        "text": "Y a-t-il des aliments que vous n’aimez pas ?",
        "type": "text",
        "category": "Nutrition"
    },

    # ---------------------- OBJECTIFS ----------------------
    {
        "id": "goal",
        "text": "Quel est votre objectif principal ?",
        "type": "choice",
        "choices": ["Perte de poids", "Prise de muscle", "Maintien de forme", "Performance sportive"],
        "category": "Objectifs"
    },
    {
        "id": "goalDetail",
        "text": "Souhaitez-vous préciser votre objectif ? (ex : gagner en endurance, stabiliser mon poids...)",
        "type": "text",
        "category": "Objectifs"
    },

    # ---------------------- RELIGION ----------------------
    {
        "id": "religiousRestrictions",
        "text": "Suivez-vous des restrictions alimentaires liées à votre religion ?",
        "type": "choice",
        "choices": ["Aucune", "Halal", "Casher", "Autre"],
        "category": "Religion"
    },

    # ---------------------- MODE DE VIE ----------------------
    {
        "id": "activityLevel",
        "text": "Quel est votre niveau d’activité physique ?",
        "type": "choice",
        "choices": ["Faible", "Modéré", "Élevé"],
        "category": "Mode de vie"
    },
    {
        "id": "sports",
        "text": "Pratiquez-vous un sport ? Si oui, lequel ou lesquels ?",
        "type": "text",
        "category": "Mode de vie"
    },
    {
        "id": "occupation",
        "text": "Quel est votre métier ou activité principale ?",
        "type": "text",
        "category": "Mode de vie"
    },
    {
        "id": "notes",
        "text": "Souhaitez-vous ajouter une précision sur votre mode de vie ? (ex : rythme de sommeil, stress...)",
        "type": "text",
        "category": "Mode de vie"
    },
]
