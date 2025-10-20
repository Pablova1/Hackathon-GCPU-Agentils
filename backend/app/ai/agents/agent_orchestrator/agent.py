"""
Agent Orchestrateur - Combine les suggestions de nutrition, fitness et médicales.

Prend les sorties du MealSuggestionAgent, du CoachAgent et du MedicalAgent,
puis génère une suggestion holistique unifiée via Google Gemini.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai


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
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        load_env: bool = True
    ):
        """
        Initialise l'agent orchestrateur.
        
        Args:
            api_key: Clé API Google Gemini
            model_name: Nom du modèle Gemini
            load_env: Si True, charge les variables d'environnement
        """
        # Charger la clé API
        if load_env:
            env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY manquante dans .env")
        
        # Configurer Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"OrchestratorAgent initialisé avec le modèle {model_name}")
    
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
        
        prompt = f"""You are a holistic health and wellness coach who provides integrated lifestyle recommendations combining nutrition, fitness, and medical considerations.

USER PROFILE:
- Age: {profile.get('age')} years old
- Gender: {profile.get('gender')}
- Weight: {profile.get('weight_kg')} kg
- Activity Level: {profile.get('activity_level')}

USER GOALS:
- Main Goal: {goals.get('mainGoal', 'General health')}
- Target Weight: {goals.get('targetWeight', 'Not specified')} kg

MEDICAL CONTEXT (from Medical Agent):
{medical_text if medical_text else "No specific medical constraints"}

NUTRITION SUGGESTION (from Meal Agent):
{meal_text}

FITNESS SUGGESTION (from Coach Agent):
{workout_text}

TASK:
Create EXACTLY ONE unified, holistic daily recommendation that combines nutrition, fitness, AND medical considerations into a coherent action plan.

REQUIREMENTS:
1. Integrate the meal, workout, and medical context into one cohesive plan
2. Ensure timing makes sense (e.g., pre/post-workout nutrition if relevant)
3. Account for medical constraints (medications, allergies, injuries)
4. Highlight how the meal supports the workout and respects medical needs
5. Keep it concise, motivating, and actionable
6. One paragraph format (2-3 sentences max)
7. Start with "Today's Plan:" or "Your Daily Focus:"

EXAMPLE OUTPUT:
Today's Plan: Given your blood pressure medication, focus on low-sodium grilled chicken with quinoa for lunch (350 kcal). Complete your 45-minute upper body strength session at moderate intensity, staying hydrated. Avoid intense cardio and prioritize potassium-rich foods like bananas post-workout.

Now generate the unified suggestion:"""
        
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
            
            unified_text = getattr(response, 'text', str(response)).strip()
            
            logger.info("Unified suggestion generated successfully")
            
            result = {
                "success": True,
                "unified_suggestion": unified_text,
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
