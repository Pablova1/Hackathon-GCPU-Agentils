"""
Modèle pour les repas (meals) scannés par les utilisateurs
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Classe helper pour gérer les ObjectId de MongoDB avec Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Nutrients(BaseModel):
    """Informations nutritionnelles d'un repas"""
    calories: Optional[float] = Field(None, description="Calories en kcal")
    protein: Optional[float] = Field(None, description="Protéines en grammes")
    fat: Optional[float] = Field(None, description="Lipides en grammes")
    carbohydrates: Optional[float] = Field(None, description="Glucides en grammes")
    fiber: Optional[float] = Field(None, description="Fibres en grammes")

    class Config:
        json_schema_extra = {
            "example": {
                "calories": 450.5,
                "protein": 35.2,
                "fat": 12.8,
                "carbohydrates": 45.3,
                "fiber": 8.5
            }
        }


class MealDocument(BaseModel):
    """Document représentant un repas dans MongoDB"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    userId: str = Field(..., description="ID de l'utilisateur propriétaire du repas")
    name: str = Field(default="", description="Nom du repas (optionnel)")
    ingredients: list[str] = Field(default_factory=list, description="Liste des ingrédients")
    nutrients: Nutrients = Field(default_factory=Nutrients, description="Informations nutritionnelles")
    dateScanned: datetime = Field(default_factory=datetime.utcnow, description="Date de scan du repas")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "68efab5a4b0f91f9f00c3196",
                "userId": "68efa5944b0f91f9f00c318d",
                "name": "Healthy Chicken Bowl",
                "ingredients": [
                    "chicken breast",
                    "quinoa",
                    "broccoli",
                    "carrots",
                    "olive oil",
                    "lemon juice"
                ],
                "nutrients": {
                    "calories": 450.5,
                    "protein": 35.2,
                    "fat": 12.8,
                    "carbohydrates": 45.3,
                    "fiber": 8.5
                },
                "dateScanned": "2025-01-15T12:30:00Z"
            }
        }


class MealCreate(BaseModel):
    """Schéma pour la création d'un nouveau repas"""
    userId: str
    name: str = ""
    ingredients: list[str] = Field(default_factory=list)
    nutrients: Optional[Nutrients] = Field(default_factory=Nutrients)

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "68efa5944b0f91f9f00c318d",
                "name": "Healthy Chicken Bowl",
                "ingredients": ["chicken breast", "quinoa", "broccoli"],
                "nutrients": {
                    "calories": 450.5,
                    "protein": 35.2,
                    "fat": 12.8,
                    "carbohydrates": 45.3,
                    "fiber": 8.5
                }
            }
        }


class MealUpdate(BaseModel):
    """Schéma pour la mise à jour d'un repas existant"""
    name: Optional[str] = None
    ingredients: Optional[list[str]] = None
    nutrients: Optional[Nutrients] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Chicken Bowl",
                "nutrients": {
                    "calories": 475.0,
                    "protein": 38.0
                }
            }
        }
