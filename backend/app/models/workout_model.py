from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['type'] = 'string'
        return json_schema

class Exercise(BaseModel):
    name: str
    duration: Optional[int] = None  # minutes
    sets: Optional[int] = None
    reps: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

class WorkoutDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    userId: str = Field(..., description="ID de l'utilisateur propriétaire de la séance")
    type: str = Field(..., description="Type d'entraînement (Cardio, Strength, etc.)")
    date: datetime = Field(default_factory=datetime.now, description="Date de la séance")
    duration_minutes: int = Field(..., description="Durée totale de la séance en minutes")
    exercises: List[Exercise] = Field(default_factory=list, description="Liste des exercices")
    intensity: Optional[str] = Field(None, description="Niveau d'intensité (Low, Moderate, High)")
    notes: Optional[str] = Field(None, description="Notes ou remarques sur la séance")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "653f1a2b8c9e4a1b2c3d4e5f",
                "userId": "user_72cd999968cb9e56",
                "type": "Cardio",
                "date": "2025-10-20T18:30:00Z",
                "duration_minutes": 45,
                "exercises": [
                    {"name": "Tapis de course", "duration": 30},
                    {"name": "Vélo elliptique", "duration": 15}
                ],
                "intensity": "Moderate",
                "notes": "Bonne séance, pas de douleur"
            }
        }
