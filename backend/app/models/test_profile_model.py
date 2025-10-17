from datetime import datetime
from profile_model import UserDocument

example = {
    "profile": {
        "lastName": "Durand",
        "firstName": "Sophie",
        "age": 28,
        "gender": "Female",
        "weight": 62,
        "height": 168,
        "bodyType": "mesomorphic"
    },
    "medical": {
        "treatments": [
            {"name": "Levothyrox", "dosage": "75 µg/day", "condition": "hypothyroidism"}
        ],
        "allergies": ["peanuts", "pollen"],
        "medicalHistory": {"personal": [], "family": []},
        "birthControl": {"uses": True, "name": "Optilova"}
    },
    "nutrition": {
        "diet": "vegetarian",
        "intolerances": ["lactose"],
        "preferences": {
            "liked": ["tofu", "avocado", "berries"],
            "disliked": ["fried food", "processed meat"],
            "general": ["organic", "high in protein"]
        }
    },
    "goals": {
        "muscleGain": True,
        "weightLoss": False,
        "goalDetail": "Increase muscle mass while improving endurance",
        "performance": False,
        "maintainShape": False
    },
    "religiousRestrictions": {"practicing": True, "type": "halal"},
    "misc": {
        "activityLevel": "moderate",
        "sports": ["fitness", "yoga"],
        "occupation": "nurse",
        "notes": "Works irregular hours, gets little sleep during the week"
    },
    "createdAt": "2025-10-15T10:42:00Z"
}

doc = UserDocument(**example)
print(doc.model_dump_json(indent=2))
