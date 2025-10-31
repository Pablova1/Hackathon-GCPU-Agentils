"""
Agent for analyzing macro-nutrients and micro-nutrients based on a list of aliments.
"""
from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent
import sys
import os

# Add parent directories to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

SYSTEM_INSTRUCTION = """
You are a nutrition expert. Analyze the list of foods provided by the user and return complete nutritional values for each food item.

For each food item, calculate nutritional information based on the indicated quantity (in grams).

Calculate:
- Macronutrients: calories, proteins, carbohydrates, lipids, fiber, sugars, saturated fats, unsaturated fats
- Main micronutrients: calcium, iron, magnesium, potassium, sodium, zinc, phosphorus, vitamin_a, vitamin_c, vitamin_d, vitamin_e, vitamin_b12

Use standard average nutritional values from reliable nutritional databases (USDA, CIQUAL, etc.). 
If a food can vary depending on preparation method (grilled, boiled, raw, etc.), use the most common preparation method.

IMPORTANT:
- All numbers must be numeric values (not strings)
- "quantity" must be an integer representing grams
- All field names must be in English
- Calculate values based on the actual quantity provided (not per 100g)
- Return valid data matching the expected schema
"""

class NutritionalValues(BaseModel):
    """Macronutrients for a specific food quantity"""
    energy_kcal: float
    proteins_g: float
    carbohydrates_g: float
    lipids_g: float
    fiber_g: float
    sugars_g: float
    saturated_fats_g: float
    unsaturated_fats_g: float

class MicronutritionalValues(BaseModel):
    """Micronutrients for a specific food quantity"""
    calcium_mg: float
    iron_mg: float
    magnesium_mg: float
    potassium_mg: float
    sodium_mg: float
    zinc_mg: float
    phosphorus_mg: float
    vitamin_a_mcg: float = 0
    vitamin_c_mg: float = 0
    vitamin_d_mcg: float = 0
    vitamin_e_mg: float = 0
    vitamin_b12_mcg: float = 0

class FoodNutrition(BaseModel):
    """Nutritional information for a single food item"""
    food: str = Field(description="Name of the food")
    quantity: int = Field(description="Quantity in grams")
    nutritional_values: NutritionalValues
    micronutrients: MicronutritionalValues

class NutrimentAnalysisResult(BaseModel):
    """Complete nutritional analysis result"""
    foods_nutrition: List[FoodNutrition]

root_agent = Agent(
    name="nutriment_analyzer_agent",
    model="gemini-2.5-flash",
    description="Agent that analyzes macro-nutrients and micro-nutrients based on a list of aliments.",
    instruction=SYSTEM_INSTRUCTION,  # Sans placeholder
    tools=[],
    output_schema=NutrimentAnalysisResult,
    output_key="nutriment_analysis_result",
)