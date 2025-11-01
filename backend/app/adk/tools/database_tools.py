"""
Database Tools for ADK Agents

These tools provide reusable database access functions
that can be used by any ADK agent.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from google.genai.types import Tool, FunctionDeclaration

# Import MongoDB client
from app.db.mongo_client import get_database


logger = logging.getLogger(__name__)


# ========================================
# MEAL HISTORY TOOL
# ========================================

async def get_user_meals(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Retrieve user's meal history from MongoDB.
    
    Args:
        user_id: User identifier (e.g., "user_abc123")
        days: Number of days to look back (default: 7)
    
    Returns:
        List of meal documents with nutrients
    """
    try:
        db = await get_database()
        meals_collection = db["meals"]
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = meals_collection.find({
            "userId": user_id,
            "dateScanned": {"$gte": start_date}
        }).sort("dateScanned", -1)
        
        meals = await cursor.to_list(length=100)
        
        logger.info(f"Retrieved {len(meals)} meals for user {user_id}")
        
        # Format for LLM consumption
        formatted_meals = []
        for meal in meals:
            nutrients = meal.get("nutrients", {})
            formatted_meals.append({
                "name": meal.get("name", "Unknown"),
                "date": meal.get("dateScanned", "")[:10],
                "calories": nutrients.get("calories", 0),
                "protein": nutrients.get("protein", 0),
                "carbs": nutrients.get("carbohydrates", 0),
                "fat": nutrients.get("fat", 0),
                "fiber": nutrients.get("fiber", 0),
                "ingredients": meal.get("ingredients", [])[:5]  # Limit ingredients
            })
        
        return formatted_meals
    
    except Exception as e:
        logger.error(f"Error retrieving meals for user {user_id}: {e}")
        return []


# ADK Tool Declaration
get_user_meals_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_user_meals",
            description="Retrieves the user's meal history from the database for analysis. Returns meals with nutritional information including calories, protein, carbs, fat, and ingredients.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID in format 'user_xxxxx'"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of meal history to retrieve (default: 7)",
                        "default": 7
                    }
                },
                "required": ["user_id"]
            }
        )
    ]
)


# ========================================
# USER PROFILE TOOL
# ========================================

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user's complete profile from MongoDB.
    
    Args:
        user_id: User identifier
    
    Returns:
        Formatted profile data including demographics, goals, preferences
    """
    try:
        db = await get_database()
        users_collection = db["user"]
        
        user = await users_collection.find_one({"user_id": user_id})
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return {"error": f"User not found: {user_id}"}
        
        # Extract data with support for both new and old schema
        profile = user.get("profile", user.get("profil", {}))
        goals = user.get("goals", user.get("objectifs", {}))
        nutrition = user.get("nutrition", user.get("alimentaire", {}))
        misc = user.get("misc", user.get("divers", {}))
        religious = user.get("religiousRestrictions", user.get("obligations_religieuses", {}))
        
        return {
            "age": profile.get("age"),
            "gender": profile.get("gender", profile.get("sexe")),
            "weight_kg": profile.get("weight", profile.get("poids")),
            "height_cm": profile.get("height", profile.get("taille")),
            "body_type": profile.get("bodyType", profile.get("morphologie")),
            "activity_level": misc.get("activityLevel", misc.get("niveau_activite", "moderate")),
            "sports": misc.get("sports", []),
            "occupation": misc.get("occupation", misc.get("profession")),
            "diet_type": nutrition.get("diet", nutrition.get("regime", "omnivore")),
            "allergies": user.get("medical", {}).get("allergies", []),
            "intolerances": nutrition.get("intolerances", []),
            "preferences": nutrition.get("preferences", []),
            "religious_practicing": religious.get("practicing", religious.get("pratique", False)),
            "religious_type": religious.get("type", ""),
            "goals": {
                "main_goal": goals.get("mainGoal", goals.get("objectif_principal", "maintain health")),
                "target_weight": goals.get("targetWeight", goals.get("poids_cible")),
                "muscle_gain": goals.get("muscleGain", goals.get("masse_musculaire", False)),
                "weight_loss": goals.get("weightLoss", goals.get("perte_de_poids", False)),
                "performance": goals.get("performance", False),
                "maintain_shape": goals.get("maintainShape", False)
            }
        }
    
    except Exception as e:
        logger.error(f"Error retrieving profile for user {user_id}: {e}")
        return {"error": str(e)}


# ADK Tool Declaration
get_user_profile_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_user_profile",
            description="Retrieves the user's complete profile including demographics, health goals, dietary preferences, and activity level. Essential for personalized recommendations.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID in format 'user_xxxxx'"
                    }
                },
                "required": ["user_id"]
            }
        )
    ]
)


# ========================================
# WORKOUT HISTORY TOOL
# ========================================

async def get_user_workouts(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Retrieve user's workout history from MongoDB.
    
    Args:
        user_id: User identifier
        days: Number of days to look back
    
    Returns:
        List of workout documents
    """
    try:
        db = await get_database()
        workouts_collection = db["workouts"]
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = workouts_collection.find({
            "userId": user_id,
            "date": {"$gte": start_date}
        }).sort("date", -1)
        
        workouts = await cursor.to_list(length=100)
        
        logger.info(f"Retrieved {len(workouts)} workouts for user {user_id}")
        
        # Format for LLM
        formatted_workouts = []
        for workout in workouts:
            formatted_workouts.append({
                "type": workout.get("type", "unknown"),
                "date": workout.get("date", "")[:10],
                "duration_minutes": workout.get("duration_minutes", 0),
                "intensity": workout.get("intensity", "moderate"),
                "exercises": workout.get("exercises", [])[:5],  # Limit exercises
                "notes": workout.get("notes", "")[:200]  # Limit notes
            })
        
        return formatted_workouts
    
    except Exception as e:
        logger.error(f"Error retrieving workouts for user {user_id}: {e}")
        return []


# ADK Tool Declaration
get_user_workouts_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_user_workouts",
            description="Retrieves the user's workout history including exercise types, duration, intensity, and exercises performed. Used for analyzing training patterns and recovery needs.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID in format 'user_xxxxx'"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of workout history to retrieve (default: 7)",
                        "default": 7
                    }
                },
                "required": ["user_id"]
            }
        )
    ]
)


# ========================================
# MEDICAL DATA TOOL
# ========================================

async def get_user_medical(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user's medical information from MongoDB.
    
    Args:
        user_id: User identifier
    
    Returns:
        Medical data including treatments, allergies, history
    """
    try:
        db = await get_database()
        users_collection = db["user"]
        
        user = await users_collection.find_one({"user_id": user_id})
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return {"error": f"User not found: {user_id}"}
        
        medical = user.get("medical", {})
        
        # Format treatments
        treatments = []
        for treatment in (medical.get("treatments") or medical.get("traitement") or []):
            if isinstance(treatment, dict):
                treatments.append({
                    "name": treatment.get("name", treatment.get("nom", "")),
                    "dosage": treatment.get("dosage", ""),
                    "condition": treatment.get("condition", treatment.get("indication", ""))
                })
            else:
                treatments.append({"name": str(treatment), "dosage": "", "condition": ""})
        
        return {
            "treatments": treatments,
            "allergies": medical.get("allergies", []),
            "injuries": medical.get("injuries", []),
            "medical_history": {
                "personal": medical.get("medicalHistory", {}).get("personal", 
                           medical.get("medicalHistory", {}).get("personnels", [])),
                "family": medical.get("medicalHistory", {}).get("family",
                         medical.get("medicalHistory", {}).get("familiaux", []))
            },
            "birth_control": medical.get("birthControl", medical.get("pilule", {}))
        }
    
    except Exception as e:
        logger.error(f"Error retrieving medical data for user {user_id}: {e}")
        return {"error": str(e)}


# ADK Tool Declaration
get_user_medical_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="get_user_medical",
            description="Retrieves the user's medical information including current treatments, allergies, injuries, and medical history. Critical for safety in nutrition and fitness recommendations.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID in format 'user_xxxxx'"
                    }
                },
                "required": ["user_id"]
            }
        )
    ]
)
