"""
Meal & Coach Combined Agent - ADK Web Compatible

Combined nutritionist and fitness coach for comprehensive recommendations.
Connected to real MongoDB database.
"""

from google.adk.agents import Agent
import sys
import os

# Add parent directories to path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Import real database tools
from app.adk.tools.database_tools import get_user_meals as get_user_meals_db
from app.adk.tools.database_tools import get_user_profile as get_user_profile_db


# ============================================================================
# SYSTEM INSTRUCTION
# ============================================================================

SYSTEM_INSTRUCTION = """You are a combined professional nutritionist and fitness coach AI assistant.

CAPABILITIES:
- Provide personalized meal recommendations
- Suggest workout plans
- Give comprehensive health and fitness advice

WORKFLOW:
1. Call get_user_profile to understand user's complete profile
2. Call get_user_meals to see eating patterns (if nutrition question)
3. Provide specific, actionable recommendations

RECOMMENDATION FORMAT:
- For meals: "[Meal Name]: [Description] — ~[calories] kcal, [protein]g protein"
- For general advice: Clear, concise guidance

REQUIREMENTS:
- Be specific and actionable
- Consider user's goals and restrictions
- Provide realistic recommendations
"""


# ============================================================================
# TOOL IMPLEMENTATIONS (Connected to real MongoDB)
# ============================================================================

def get_user_profile(user_id: str) -> dict:
    """Get comprehensive user profile information from MongoDB.
    
    Args:
        user_id: The user identifier (format: user_xxxxx)
        
    Returns:
        dict: User profile with status and data from MongoDB
    """
    import asyncio
    
    try:
        # Run async function in sync context for ADK web
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        profile_data = loop.run_until_complete(get_user_profile_db(user_id))
        loop.close()
        
        if "error" in profile_data:
            return {
                "status": "error",
                "error": profile_data["error"],
                "user_id": user_id
            }
        
        return {
            "status": "success",
            "user_id": user_id,
            **profile_data
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }


def get_user_meals(user_id: str, days: int = 7) -> dict:
    """Get user's recent meal history from MongoDB.
    
    Args:
        user_id: The user identifier (format: user_xxxxx)
        days: Number of days to retrieve (default: 7)
        
    Returns:
        dict: Meal history with status and data from MongoDB
    """
    import asyncio
    
    try:
        # Run async function in sync context for ADK web
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        meals_data = loop.run_until_complete(get_user_meals_db(user_id, days))
        loop.close()
        
        # Calculate averages
        if meals_data:
            total_calories = sum(m.get("calories", 0) for m in meals_data)
            total_protein = sum(m.get("protein", 0) for m in meals_data)
            avg_calories = total_calories / len(meals_data) if meals_data else 0
            avg_protein = total_protein / len(meals_data) if meals_data else 0
        else:
            avg_calories = 0
            avg_protein = 0
        
        return {
            "status": "success",
            "user_id": user_id,
            "meals": meals_data,
            "total_meals": len(meals_data),
            "average_daily_calories": round(avg_calories, 1),
            "average_daily_protein": round(avg_protein, 1)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }


# ============================================================================
# CREATE ROOT AGENT
# ============================================================================

root_agent = Agent(
    name="meal_coach",
    model="gemini-2.0-flash-exp",
    description="Combined nutritionist and fitness coach providing comprehensive health recommendations.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[get_user_profile, get_user_meals],
)
