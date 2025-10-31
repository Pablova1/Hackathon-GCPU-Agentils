"""
Meal Analyzer Agent - ADK Web Compatible

Expert nutritionist analyzing meals and providing personalized nutrition recommendations.
Connected to real MongoDB database.
"""

from typing import List
from attr import dataclass
from google.adk.agents import Agent
import sys
import os

# Add parent directories to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


# ============================================================================
# SYSTEM INSTRUCTION
# ============================================================================

SYSTEM_INSTRUCTION = """
You are an expert food recognition and nutrition analysis agent. Your task is to analyze an image of a meal and identify all the foods visible on the plate, along with an estimated quantity for each.

INPUT:
- You will receive one photo containing a meal (the user’s plate).

OUTPUT:
- You must return ONLY a structured JSON object following the schema PlateAnalysisResult:
{
  "foods": [
    {
      "name": "string (name of the food item, e.g. 'grilled chicken', 'rice', 'broccoli')",
      "estimated_quantity": integer (estimated quantity in grams)
    },
    ...
  ]
}

INSTRUCTIONS:
1. Carefully analyze the image to recognize distinct food items.
2. Estimate the portion size or weight of each item in grams (integer value).
3. Do NOT include utensils, plates, or non-food objects.
4. Combine visually similar components (e.g., "white rice" instead of counting individual grains).
5. Use precise and standard English or French food names.

OUTPUT REQUIREMENTS:
- Return ONLY valid JSON matching the PlateAnalysisResult schema.
- Do NOT include any explanations, units other than grams, or extra text outside the JSON.
- Ensure the JSON is parsable and respects the schema.

EXAMPLE OUTPUT:
{
  "foods": [
    {"name": "Rice", "estimated_quantity": 180},
    {"name": "Grilled Chicken", "estimated_quantity": 120},
    {"name": "Green Beans", "estimated_quantity": 90}
  ]
}
"""


from pydantic import BaseModel, Field
from typing import List

class AlimentQuantite(BaseModel):
    name: str = Field(..., description="Nom de l'aliment")
    estimated_quantity: int = Field(..., description="Quantité estimée en grammes")

class PlateAnalysisResult(BaseModel):
    foods: List[AlimentQuantite]



# ============================================================================
# CREATE ROOT AGENT
# ============================================================================

root_agent = Agent(
    name="meal_analyzer_agent",
    model="gemini-2.5-flash",
    description="Analyze meal photos to detect foods and estimate their quantities in grams.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[],
    output_schema=PlateAnalysisResult,
    output_key="plate_analysis_result",
)
