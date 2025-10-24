"""
Agent Orchestrateur - Combine les suggestions de nutrition, fitness et médicales.

Prend les sorties du MealSuggestionAgent, du CoachAgent et du MedicalAgent,
puis génère une suggestion holistique unifiée via Google Gemini sur Vertex AI.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel
import vertexai


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Agent orchestrateur qui combine les suggestions de nutrition, fitness
    et médicales en une recommandation holistique cohérente.
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-001",
        load_env: bool = True
    ):
        """
        Initialise l'agent orchestrateur.
        
        Args:
            project_id: Google Cloud Project ID
            location: Google Cloud Location (e.g., 'us-central1')
            model_name: Nom du modèle Gemini
            load_env: Si True, charge les variables d'environnement
        """
        # Charger les variables d'environnement
        if load_env:
            env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location or os.getenv("GCP_LOCATION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID manquant dans .env")
        
        # Initialiser Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model_name = model_name
        self.model = GenerativeModel(model_name)
        
        logger.info(f"OrchestratorAgent initialisé avec le modèle {model_name} sur Vertex AI")
        logger.info(f"Project: {self.project_id}, Location: {self.location}")
    
    def build_orchestration_prompt(
        self,
        meal_suggestion: Dict[str, Any],
        workout_suggestion: Dict[str, Any],
        medical_context: Optional[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> str:
        """
        Construit le prompt pour combiner les suggestions.
        
        Args:
            meal_suggestion: Résultat du MealSuggestionAgent
            workout_suggestion: Résultat du CoachAgent
            medical_context: Résultat du MedicalAgent (optionnel)
            user_context: Contexte utilisateur (profil + objectifs)
            
        Returns:
            Prompt formaté pour Gemini
        """
        meal_text = meal_suggestion.get("suggestion", "No meal suggestion available")
        workout_text = workout_suggestion.get("suggestion", "No workout suggestion available")
        medical_text = ""
        
        if medical_context and medical_context.get("success", False):
            medical_text = medical_context.get("medical_analysis", "")
        
        profile = user_context.get("profile", {})
        goals = user_context.get("goals", {})
        
        # Récupérer les statistiques d'entraînement et de nutrition
        workout_stats = workout_suggestion.get("user_context", {}).get("workout_statistics", {})
        meal_stats = meal_suggestion.get("user_context", {}).get("period_statistics", {})
        
        prompt = f"""You are an orchestrator agent that analyzes user data on training, nutrition, and health to generate two distinct outputs.

## Context
USER PROFILE:
- Age: {profile.get('age')} years old
- Gender: {profile.get('gender')}
- Weight: {profile.get('weight_kg')} kg
- Activity Level: {profile.get('activity_level')}

USER GOALS:
- Main Goal: {goals.get('mainGoal', 'General health')}
- Target Weight: {goals.get('targetWeight', 'Not specified')} kg

RECENT WORKOUT DATA:
- Frequency: {workout_stats.get('frequency_per_week', 0)} workouts/week
- Consistency: {workout_stats.get('consistency', 'unknown')}
- Total workouts: {workout_stats.get('total_workouts', 0)}

RECENT NUTRITION DATA:
- Total meals recorded: {meal_stats.get('total_meals', 0)}
- Average calories: {meal_stats.get('totals', {}).get('calories', 0) / max(meal_stats.get('total_meals', 1), 1):.0f} kcal/meal

MEDICAL CONTEXT:
{medical_text if medical_text else "No specific medical constraints"}

NUTRITION SUGGESTION (from Meal Agent):
{meal_text}

FITNESS SUGGESTION (from Coach Agent):
{workout_text}

## Required Outputs

### 1. Motivation Message (string)
Generate ONE synthetic and encouraging sentence that:
- Assesses the person's current overall fitness state
- Is supportive and wellness-oriented
- Remains positive and motivating
- Is concise (max 2 short sentences)

Examples:
- "You're in great shape, good recovery and healthy life! Keep going!"
- "Your training is consistent and nutrition is balanced. Your body is responding well!"
- "Take it easy this week, your body needs some rest. Recovery is progress too!"

### 2. Meal Suggestions (array)
Generate a list of **5 suggested meals** adapted to the user's profile that:
- Match their current nutritional needs
- Are varied and balanced (different meal types: breakfast, lunch, dinner, snack)
- Account for their physical activity level
- Consider their recovery state (higher protein if intense training, lighter meals if rest day)

Each meal must include:
- id (1-5)
- name
- description (short)
- calories (realistic number)
- macros (protein, carbs, fat in grams)
- meal_type (breakfast, lunch, dinner, or snack)

## IMPORTANT: Return ONLY a valid JSON object with this EXACT structure:
{{
  "motivation_message": "Your personalized motivating message here",
  "meal_suggestions": [
    {{
      "id": 1,
      "name": "Meal name",
      "description": "Short meal description",
      "calories": 650,
      "macros": {{"protein": 45, "carbs": 60, "fat": 20}},
      "meal_type": "breakfast"
    }},
    {{
      "id": 2,
      "name": "Another meal",
      "description": "Description",
      "calories": 580,
      "macros": {{"protein": 42, "carbs": 50, "fat": 18}},
      "meal_type": "lunch"
    }},
    {{
      "id": 3,
      "name": "Third meal",
      "description": "Description",
      "calories": 520,
      "macros": {{"protein": 38, "carbs": 45, "fat": 20}},
      "meal_type": "dinner"
    }},
    {{
      "id": 4,
      "name": "Fourth meal",
      "description": "Description",
      "calories": 320,
      "macros": {{"protein": 25, "carbs": 35, "fat": 8}},
      "meal_type": "snack"
    }},
    {{
      "id": 5,
      "name": "Fifth meal",
      "description": "Description",
      "calories": 480,
      "macros": {{"protein": 35, "carbs": 55, "fat": 15}},
      "meal_type": "breakfast"
    }}
  ]
}}

CRITICAL: Return ONLY the JSON object, no additional text, no markdown, no explanation. Just the raw JSON."""
        
        return prompt
    
    def orchestrate(
        self,
        meal_suggestion: Dict[str, Any],
        workout_suggestion: Dict[str, Any],
        medical_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestre et combine les suggestions de nutrition, fitness et médicales.
        
        Args:
            meal_suggestion: Résultat du MealSuggestionAgent
            workout_suggestion: Résultat du CoachAgent
            medical_context: Résultat du MedicalAgent (optionnel)
            user_context: Contexte utilisateur optionnel (profil + objectifs)
            
        Returns:
            Dict contenant la suggestion unifiée et les suggestions individuelles
        """
        try:
            logger.info("Orchestrating meal, workout, and medical suggestions...")
            
            # Vérifier que les agents essentiels ont réussi
            if not meal_suggestion.get("success", False):
                return {
                    "success": False,
                    "error": f"Meal suggestion failed: {meal_suggestion.get('error')}",
                    "generated_at": datetime.now().isoformat()
                }
            
            if not workout_suggestion.get("success", False):
                return {
                    "success": False,
                    "error": f"Workout suggestion failed: {workout_suggestion.get('error')}",
                    "generated_at": datetime.now().isoformat()
                }
            
            # Le contexte médical est optionnel - continuer même s'il a échoué
            if medical_context and not medical_context.get("success", False):
                logger.warning(f"Medical context unavailable: {medical_context.get('error')}")
                medical_context = None
            
            # Extraire le contexte utilisateur si disponible
            if user_context is None:
                user_context = {
                    "profile": meal_suggestion.get("user_context", {}).get("profile", {}),
                    "goals": meal_suggestion.get("user_context", {}).get("goals", {})
                }
            
            # Construire le prompt
            prompt = self.build_orchestration_prompt(
                meal_suggestion,
                workout_suggestion,
                medical_context,
                user_context
            )
            
            # Appeler Gemini pour orchestration
            logger.info(f"Calling Gemini ({self.model_name}) for orchestration...")
            response = self.model.generate_content(prompt)
            
            raw_text = getattr(response, 'text', str(response)).strip()
            
            # Parser le JSON retourné par Gemini
            import json
            import re
            
            # Nettoyer le texte pour extraire uniquement le JSON
            # Supprimer les balises markdown si présentes
            json_text = raw_text
            if "```json" in json_text:
                json_text = re.search(r'```json\s*(\{.*?\})\s*```', json_text, re.DOTALL)
                if json_text:
                    json_text = json_text.group(1)
            elif "```" in json_text:
                json_text = re.search(r'```\s*(\{.*?\})\s*```', json_text, re.DOTALL)
                if json_text:
                    json_text = json_text.group(1)
            
            # Parser le JSON
            try:
                orchestrated_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Gemini: {e}")
                logger.error(f"Raw text: {raw_text}")
                # Fallback: retourner un format par défaut
                orchestrated_data = {
                    "motivation_message": "Keep up the great work! Stay consistent with your nutrition and training.",
                    "meal_suggestions": []
                }
            
            logger.info("Unified suggestion generated successfully")
            
            result = {
                "success": True,
                "motivation_message": orchestrated_data.get("motivation_message", ""),
                "meal_suggestions": orchestrated_data.get("meal_suggestions", []),
                "individual_suggestions": {
                    "meal": {
                        "suggestion": meal_suggestion.get("suggestion"),
                        "generated_at": meal_suggestion.get("generated_at")
                    },
                    "workout": {
                        "suggestion": workout_suggestion.get("suggestion"),
                        "generated_at": workout_suggestion.get("generated_at")
                    }
                },
                "user_context": user_context,
                "generated_at": datetime.now().isoformat()
            }
            
            # Ajouter le contexte médical s'il est disponible
            if medical_context:
                result["individual_suggestions"]["medical"] = {
                    "analysis": medical_context.get("medical_analysis"),
                    "generated_at": medical_context.get("generated_at")
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error orchestrating suggestions: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error orchestrating suggestions: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
