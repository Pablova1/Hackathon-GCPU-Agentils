"""
Pure ADK Main Orchestrator

Uses google.adk.agents.Agent() for complete ADK integration.
Coordinates meal, workout, and medical agents to generate unified suggestions.
"""

import logging
import json
import asyncio
from datetime import datetime
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.adk.config import get_config
from app.adk.agent_registry import get_meal_agent, get_coach_agent, get_medical_agent


logger = logging.getLogger(__name__)


# ============================================================================
# AGENT WRAPPER FUNCTIONS
# ============================================================================

async def generate_meal_suggestion(user_id: str, days: int = 7) -> dict:
    """
    Generate meal suggestion using the meal agent from agent_registry.
    
    Args:
        user_id: User identifier
        days: Days of history to analyze
        
    Returns:
        Dict with success status and suggestion
    """
    try:
        meal_agent = get_meal_agent()
        
        # Create session service and runner
        session_service = InMemorySessionService()
        app_name = "meal_agent_app"
        session_id = f"meal_session_{user_id}"
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=meal_agent,
            app_name=app_name,
            session_service=session_service
        )
        
        # Create user message
        content = types.Content(
            role='user',
            parts=[types.Part(text=f"Generate a personalized meal suggestion for user {user_id} based on the last {days} days of meals.")]
        )
        
        # Run agent
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None,
            lambda: list(runner.run(user_id=user_id, session_id=session_id, new_message=content))
        )
        
        # Extract response
        suggestion = ""
        for event in events:
            if event.is_final_response() and event.content:
                suggestion = event.content.parts[0].text.strip()
                break
        
        return {
            "success": True,
            "suggestion": suggestion,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in meal agent: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }


async def generate_workout_suggestion(user_id: str, days: int = 7) -> dict:
    """
    Generate workout suggestion using the coach agent from agent_registry.
    
    Args:
        user_id: User identifier
        days: Days of history to analyze
        
    Returns:
        Dict with success status and suggestion
    """
    try:
        coach_agent = get_coach_agent()
        
        # Create session service and runner
        session_service = InMemorySessionService()
        app_name = "coach_agent_app"
        session_id = f"coach_session_{user_id}"
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=coach_agent,
            app_name=app_name,
            session_service=session_service
        )
        
        # Create user message
        content = types.Content(
            role='user',
            parts=[types.Part(text=f"Generate a personalized workout suggestion for user {user_id} based on the last {days} days of training.")]
        )
        
        # Run agent
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None,
            lambda: list(runner.run(user_id=user_id, session_id=session_id, new_message=content))
        )
        
        # Extract response
        suggestion = ""
        for event in events:
            if event.is_final_response() and event.content:
                suggestion = event.content.parts[0].text.strip()
                break
        
        return {
            "success": True,
            "suggestion": suggestion,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in coach agent: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }


async def generate_medical_analysis(user_id: str) -> dict:
    """
    Generate medical analysis using the medical agent from agent_registry.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict with success status and medical analysis
    """
    try:
        medical_agent = get_medical_agent()
        
        # Create session service and runner
        session_service = InMemorySessionService()
        app_name = "medical_agent_app"
        session_id = f"medical_session_{user_id}"
        
        # Create session
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=medical_agent,
            app_name=app_name,
            session_service=session_service
        )
        
        # Create user message
        content = types.Content(
            role='user',
            parts=[types.Part(text=f"Analyze the medical context for user {user_id} and provide safety guidance for nutrition and fitness.")]
        )
        
        # Run agent
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None,
            lambda: list(runner.run(user_id=user_id, session_id=session_id, new_message=content))
        )
        
        # Extract response
        analysis = ""
        for event in events:
            if event.is_final_response() and event.content:
                analysis = event.content.parts[0].text.strip()
                break
        
        return {
            "success": True,
            "medical_analysis": analysis,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in medical agent: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }


# ============================================================================
# ORCHESTRATOR SYSTEM INSTRUCTION
# ============================================================================

ORCHESTRATOR_INSTRUCTION = """You are an orchestrator analyzing user health data to generate two outputs.

TASK:
Generate exactly two outputs:

1. **motivation_message** (string): ONE encouraging sentence about their overall wellness state
   - Assess current fitness state based on the inputs
   - Supportive and positive tone
   - Max 2 short sentences
   Examples:
   - "You're in great shape, good recovery and healthy life! Keep going!"
   - "Your training is consistent and nutrition is balanced. Keep it up!"
   - "Take it easy this week, your body needs some rest. Recovery is progress!"

2. **meal_suggestions** (array of 5 meals): Varied meal ideas adapted to their profile
   - 5 different meals (breakfast, lunch, dinner, snack variations)
   - Balanced macros based on their activity level
   - Variety in types
   - Each meal must have: id (1-5), name, description, calories, macros {protein, carbs, fat}, meal_type

Return ONLY valid JSON with this exact structure:
{
  "motivation_message": "Your message here",
  "meal_suggestions": [
    {
      "id": 1,
      "name": "Meal name",
      "description": "Description",
      "calories": 600,
      "macros": {"protein": 40, "carbs": 55, "fat": 20},
      "meal_type": "breakfast"
    },
    {
      "id": 2,
      "name": "Another meal",
      "description": "Description",
      "calories": 550,
      "macros": {"protein": 38, "carbs": 50, "fat": 18},
      "meal_type": "lunch"
    },
    {
      "id": 3,
      "name": "Third meal",
      "description": "Description",
      "calories": 520,
      "macros": {"protein": 35, "carbs": 48, "fat": 19},
      "meal_type": "dinner"
    },
    {
      "id": 4,
      "name": "Fourth meal",
      "description": "Description",
      "calories": 300,
      "macros": {"protein": 22, "carbs": 30, "fat": 10},
      "meal_type": "snack"
    },
    {
      "id": 5,
      "name": "Fifth meal",
      "description": "Description",
      "calories": 480,
      "macros": {"protein": 32, "carbs": 52, "fat": 16},
      "meal_type": "breakfast"
    }
  ]
}

Return ONLY the JSON object, no markdown, no extra text.
"""


# ============================================================================
# PURE ADK ORCHESTRATOR
# ============================================================================

def create_adk_orchestrator() -> Agent:
    """
    Create pure ADK Orchestrator Agent.
    
    Returns:
        Agent: Configured ADK orchestrator
    """
    from google.genai import types
    config = get_config()
    
    agent = Agent(
        name="orchestrator_agent",
        model=config.orchestrator_config["model"],
        instruction=ORCHESTRATOR_INSTRUCTION,
        generate_content_config=types.GenerateContentConfig(
            temperature=config.orchestrator_config["temperature"],
            max_output_tokens=config.orchestrator_config["max_output_tokens"],
            response_mime_type="application/json"
        )
    )
    
    return agent


async def orchestrate_suggestions(user_id: str, days: int = 7) -> dict:
    """
    Orchestrate all agents to generate unified personalized suggestions using pure ADK.
    
    This uses Agent() from google.adk.agents for all coordination.
    
    Args:
        user_id: User identifier
        days: Days of history to analyze
    
    Returns:
        Dict containing motivation message and meal suggestions
    """
    try:
        logger.info(f"Starting pure ADK orchestration for user {user_id}")
        
        # Step 1: Run all three specialized agents in parallel
        meal_task = generate_meal_suggestion(user_id, days)
        workout_task = generate_workout_suggestion(user_id, days)
        medical_task = generate_medical_analysis(user_id)
        
        meal_result, workout_result, medical_result = await asyncio.gather(
            meal_task, workout_task, medical_task
        )
        
        # Check if essential agents succeeded
        if not meal_result.get("success"):
            logger.error(f"Meal agent failed: {meal_result.get('error')}")
            return {
                "success": False,
                "error": f"Meal suggestion failed: {meal_result.get('error')}",
                "generated_at": datetime.now().isoformat()
            }
        
        if not workout_result.get("success"):
            logger.error(f"Workout agent failed: {workout_result.get('error')}")
            return {
                "success": False,
                "error": f"Workout suggestion failed: {workout_result.get('error')}",
                "generated_at": datetime.now().isoformat()
            }
        
        # Medical agent is optional - continue even if it fails
        if not medical_result.get("success"):
            logger.warning(f"Medical agent failed: {medical_result.get('error')}")
            medical_text = "No specific medical constraints identified"
        else:
            medical_text = medical_result.get("medical_analysis", "")
        
        # Step 2: Synthesize with ADK orchestrator agent
        meal_text = meal_result.get("suggestion", "")
        workout_text = workout_result.get("suggestion", "")
        
        logger.info(f"Synthesizing results with pure ADK orchestrator")
        
        # Build synthesis prompt
        synthesis_prompt = f"""INPUTS:
1. NUTRITION: {meal_text}
2. FITNESS: {workout_text}
3. MEDICAL: {medical_text}

USER: {user_id}

Generate the motivation_message and meal_suggestions JSON output."""

        # Create orchestrator agent
        orchestrator = create_adk_orchestrator()
        
        # Use Runner for orchestrator
        session_service = InMemorySessionService()
        app_name = "orchestrator_app"
        session_id = f"orch_session_{user_id}"
        
        # Create session (await it properly)
        loop = asyncio.get_event_loop()
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Create runner
        runner = Runner(
            agent=orchestrator,
            app_name=app_name,
            session_service=session_service
        )
        
        # Create content message
        content = types.Content(
            role='user',
            parts=[types.Part(text=synthesis_prompt)]
        )
        
        # Run orchestrator in async context
        events = await loop.run_in_executor(
            None,
            lambda: list(runner.run(user_id=user_id, session_id=session_id, new_message=content))
        )
        
        # Extract response from events
        raw_text = ""
        for event in events:
            if event.is_final_response() and event.content:
                raw_text = event.content.parts[0].text.strip()
                break
        
        # Parse JSON
        try:
            # Clean up response
            if "```json" in raw_text:
                import re
                match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                if match:
                    raw_text = match.group(1)
            elif "```" in raw_text:
                import re
                match = re.search(r'```\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
                if match:
                    raw_text = match.group(1)
            
            synthesized_data = json.loads(raw_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from orchestration: {e}")
            logger.error(f"Raw text: {raw_text}")
            # Fallback
            synthesized_data = {
                "motivation_message": "Keep up the great work! Stay consistent with your nutrition and training.",
                "meal_suggestions": []
            }
        
        logger.info("Pure ADK orchestration completed successfully")
        
        # Build result in expected format
        result = {
            "success": True,
            "motivation_message": synthesized_data.get("motivation_message", ""),
            "meal_suggestions": synthesized_data.get("meal_suggestions", []),
            "individual_suggestions": {
                "meal": {
                    "suggestion": meal_text,
                    "generated_at": datetime.now().isoformat()
                },
                "workout": {
                    "suggestion": workout_text,
                    "generated_at": datetime.now().isoformat()
                },
                "medical": {
                    "analysis": medical_text,
                    "generated_at": datetime.now().isoformat()
                }
            },
            "generated_at": datetime.now().isoformat(),
            "method": "pure_adk"
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error in pure ADK orchestration: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Orchestration error: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }


# ============================================================================
# SINGLETON INSTANCE (for reuse)
# ============================================================================

_orchestrator_instance = None

def get_orchestrator() -> Agent:
    """Get or create singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = create_adk_orchestrator()
    return _orchestrator_instance
