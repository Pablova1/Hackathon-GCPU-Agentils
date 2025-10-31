"""
Medical Agent - ADK Web Compatible

Expert medical advisor for safe nutrition and fitness recommendations.
Connected to real MongoDB database.
"""

from google.adk.agents import Agent
from pydantic import BaseModel, Field
import sys
import os

# Add parent directories to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Import real database tools
from app.adk.tools.database_tools import get_user_medical as get_user_medical_db
from app.adk.tools.database_tools import get_user_profile as get_user_profile_db


# ============================================================================
# OUTPUT SCHEMA (Pydantic Model)
# ============================================================================

class MedicalAnalysis(BaseModel):
    """Structured output for medical analysis."""
    has_medical_constraints: bool = Field(
        description="Whether the user has any medical constraints (medications, conditions, allergies)"
    )
    key_medications: list[str] = Field(
        description="List of current medications that may affect nutrition/fitness",
        default_factory=list
    )
    key_allergies: list[str] = Field(
        description="List of serious allergies to highlight",
        default_factory=list
    )
    exercise_restrictions: list[str] = Field(
        description="List of exercise restrictions or contraindications",
        default_factory=list
    )
    dietary_restrictions: list[str] = Field(
        description="List of dietary restrictions due to medical reasons",
        default_factory=list
    )
    medical_context: str = Field(
        description="Single paragraph starting with 'Medical Context:' containing key health considerations (2-3 sentences)"
    )


# ============================================================================
# SYSTEM INSTRUCTION
# ============================================================================

SYSTEM_INSTRUCTION = """You are an expert medical advisor specializing in personalized health recommendations for nutrition and fitness programs.

WORKFLOW:
1. Call get_user_profile to understand basic demographics and health goals
2. Call get_user_medical to retrieve medical history, treatments, allergies, and conditions
3. Analyze medical constraints that affect nutrition and exercise
4. Provide structured medical guidance

OUTPUT FORMAT:
You MUST respond with a JSON object containing these fields:
- has_medical_constraints: boolean indicating if there are any medical constraints
- key_medications: array of current medications affecting nutrition/fitness (empty array if none)
- key_allergies: array of serious allergies (empty array if none)
- exercise_restrictions: array of exercise restrictions (empty array if none)
- dietary_restrictions: array of dietary restrictions due to medical reasons (empty array if none)
- medical_context: Single paragraph starting with "Medical Context:" (2-3 sentences)

Example output:
{
  "has_medical_constraints": true,
  "key_medications": ["Blood pressure medication"],
  "key_allergies": ["Peanuts", "Shellfish"],
  "exercise_restrictions": ["Avoid intense cardio without clearance", "Low-impact only for knee"],
  "dietary_restrictions": ["Monitor sodium intake", "Avoid potassium-rich foods"],
  "medical_context": "Medical Context: Patient on blood pressure medication should monitor sodium intake and avoid intense cardio without medical clearance. Prioritize potassium-rich foods and stay well-hydrated. Previous knee injury requires low-impact exercises."
}

SAFETY:
- Always mention medication interactions with food/exercise
- Highlight serious allergies prominently
- Recommend medical clearance when appropriate
- Note any contraindicated exercises or foods
"""


# ============================================================================
# CREATE ROOT AGENT
# ============================================================================

root_agent = Agent(
    name="medical_agent",
    model="gemini-2.0-flash-exp",
    description="Expert medical advisor providing safety guidance for nutrition and fitness based on medical history.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[get_user_profile_db, get_user_medical_db],
    output_schema=MedicalAnalysis,  # Enforce structured JSON output
)
