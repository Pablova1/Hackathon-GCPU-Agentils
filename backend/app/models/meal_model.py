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
    def __get_pydantic_json_schema__(cls, schema, handler):
        """Compatible avec Pydantic v2"""
        json_schema = handler(schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['type'] = 'string'
        return json_schema


class Micronutrients(BaseModel):
    """Micronutriments d'un repas"""
    calcium_mg: Optional[float] = Field(None, description="Calcium en mg")
    iron_mg: Optional[float] = Field(None, description="Fer en mg")
    magnesium_mg: Optional[float] = Field(None, description="Magnésium en mg")
    potassium_mg: Optional[float] = Field(None, description="Potassium en mg")
    sodium_mg: Optional[float] = Field(None, description="Sodium en mg")
    zinc_mg: Optional[float] = Field(None, description="Zinc en mg")
    phosphorus_mg: Optional[float] = Field(None, description="Phosphore en mg")

    class Config:
        json_schema_extra = {
            "example": {
                "calcium_mg": 57.1,
                "iron_mg": 2.0,
                "magnesium_mg": 104.8,
                "potassium_mg": 844.4,
                "sodium_mg": 136.4,
                "zinc_mg": 2.1,
                "phosphorus_mg": 435.8
            }
        }


class Nutrients(BaseModel):
    """Informations nutritionnelles complètes d'un repas"""
    energy_kcal: Optional[float] = Field(None, description="Énergie en kcal")
    proteins_g: Optional[float] = Field(None, description="Protéines en grammes")
    carbohydrates_g: Optional[float] = Field(None, description="Glucides en grammes")
    lipids_g: Optional[float] = Field(None, description="Lipides totaux en grammes")
    fiber_g: Optional[float] = Field(None, description="Fibres en grammes")
    sugars_g: Optional[float] = Field(None, description="Sucres en grammes")
    saturated_fats_g: Optional[float] = Field(None, description="Acides gras saturés en grammes")
    unsaturated_fats_g: Optional[float] = Field(None, description="Acides gras insaturés en grammes")
    micronutrients: Optional[Micronutrients] = Field(default_factory=Micronutrients, description="Micronutriments")

    class Config:
        json_schema_extra = {
            "example": {
                "energy_kcal": 398.5,
                "proteins_g": 51.0,
                "carbohydrates_g": 28.8,
                "lipids_g": 6.6,
                "fiber_g": 4.2,
                "sugars_g": 1.3,
                "saturated_fats_g": 1.73,
                "unsaturated_fats_g": 4.89,
                "micronutrients": {
                    "calcium_mg": 57.1,
                    "iron_mg": 2.0,
                    "magnesium_mg": 104.8,
                    "potassium_mg": 844.4,
                    "sodium_mg": 136.4,
                    "zinc_mg": 2.1,
                    "phosphorus_mg": 435.8
                }
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
                    "energy_kcal": 398.5,
                    "proteins_g": 51.0,
                    "carbohydrates_g": 28.8,
                    "lipids_g": 6.6,
                    "fiber_g": 4.2,
                    "sugars_g": 1.3,
                    "saturated_fats_g": 1.73,
                    "unsaturated_fats_g": 4.89,
                    "micronutrients": {
                        "calcium_mg": 57.1,
                        "iron_mg": 2.0,
                        "magnesium_mg": 104.8,
                        "potassium_mg": 844.4,
                        "sodium_mg": 136.4,
                        "zinc_mg": 2.1,
                        "phosphorus_mg": 435.8
                    }
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
                    "energy_kcal": 398.5,
                    "proteins_g": 51.0,
                    "carbohydrates_g": 28.8,
                    "lipids_g": 6.6,
                    "fiber_g": 4.2,
                    "sugars_g": 1.3,
                    "saturated_fats_g": 1.73,
                    "unsaturated_fats_g": 4.89
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
                    "energy_kcal": 475.0,
                    "proteins_g": 38.0
                }
            }
        }
