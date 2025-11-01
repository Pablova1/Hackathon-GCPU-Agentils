"""
Pydantic models for ADK agent structured outputs.

Place all agent output schemas here for reusability and clarity.
"""

from pydantic import BaseModel, Field
from typing import List

class WorkoutSuggestion(BaseModel):
    """Structured output for workout suggestions."""
    workout_type: str = Field(..., description="Type of workout (e.g., Upper Body Strength, Cardio, Full Body, etc.)")
    description: str = Field(..., description="Brief description with key exercises (e.g., '5x5 bench press, pull-ups, overhead press')")
    duration_minutes: int = Field(..., ge=15, le=180, description="Estimated duration in minutes")
    intensity: str = Field(..., description="Intensity level: Low, Medium, High, or Rest Day")
    full_suggestion: str = Field(..., description="Complete formatted suggestion line in the format: '[Workout Type]: [Description] — ~[duration]min, [Intensity]'")

class MealSuggestion(BaseModel):
    """Structured output for meal suggestions."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Grilled Salmon Bowl', 'Protein Pancakes')")
    description: str = Field(..., description="Brief description of the meal components")
    calories: int = Field(..., ge=100, le=2000, description="Estimated calories")
    protein_grams: int = Field(..., ge=0, le=200, description="Protein content in grams")
    full_suggestion: str = Field(..., description="Complete formatted suggestion line in the format: '[Meal Name]: [Description] — ~[calories] kcal, [protein]g protein'")

class MedicalAnalysis(BaseModel):
    """Structured output for medical analysis."""
    has_medical_constraints: bool = Field(..., description="Whether the user has any medical constraints (medications, conditions, allergies)")
    key_medications: List[str] = Field(default_factory=list, description="List of current medications that may affect nutrition/fitness")
    key_allergies: List[str] = Field(default_factory=list, description="List of serious allergies to highlight")
    exercise_restrictions: List[str] = Field(default_factory=list, description="List of exercise restrictions or contraindications")
    dietary_restrictions: List[str] = Field(default_factory=list, description="List of dietary restrictions due to medical reasons")
    medical_context: str = Field(..., description="Single paragraph starting with 'Medical Context:' containing key health considerations (2-3 sentences)")
