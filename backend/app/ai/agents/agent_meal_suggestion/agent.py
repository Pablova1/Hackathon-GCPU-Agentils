"""
Agent de suggestions de repas personnalisées basé sur l'historique utilisateur.

Utilise Google Gemini sur Vertex AI pour générer des recommandations alimentaires intelligentes
en analysant le profil utilisateur, ses objectifs de santé et son historique récent.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel
import vertexai
from bson import ObjectId


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MealSuggestionAgent:
    """
    Agent qui génère des suggestions de repas personnalisées en analysant
    le profil utilisateur, ses objectifs de santé et son historique alimentaire.
    
    Compatible avec les deux structures MongoDB:
    - Structure nouvelle: profile, nutrition, goals, misc
    - Structure ancienne: profil, alimentaire, objectifs, divers
    """
    
    def __init__(
        self,
        mongo_db,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-001",
        load_env: bool = True
    ):
        """
        Initialise l'agent de suggestion de repas.
        
        Args:
            mongo_db: Instance de la base MongoDB
            project_id: Google Cloud Project ID
            location: Google Cloud Location (e.g., 'us-central1')
            model_name: Nom du modèle Gemini à utiliser
            load_env: Si True, charge les variables d'environnement depuis .env
        """
        if load_env:
            # Remonter 6 niveaux pour atteindre la racine du projet
            # agent.py -> agent_meal_suggestion -> agents -> ai -> app -> backend -> PROJECT_ROOT
            env_path = Path(__file__).parent.parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        # Configuration MongoDB
        self.db = mongo_db
        self.users_collection = mongo_db.get_collection("user")
        self.meals_collection = mongo_db.get_collection("meals")
        
        # Configuration Vertex AI
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.location = location or os.getenv('GCP_LOCATION', 'us-central1')
        
        if not self.project_id:
            raise ValueError(
                "GCP_PROJECT_ID manquant. "
                "Définissez GCP_PROJECT_ID dans .env"
            )
        
        # Initialiser Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        self.model_name = model_name
        self.model = GenerativeModel(model_name)
        
        logger.info(f"MealSuggestionAgent initialisé avec le modèle {model_name} sur Vertex AI")
        logger.info(f"Project: {self.project_id}, Location: {self.location}")
    
    async def get_user_context(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Récupère le contexte complet d'un utilisateur avec son historique de repas.
        
        Args:
            user_id: ID de l'utilisateur (string format "user_xxxxx")
            days: Nombre de jours d'historique à récupérer (défaut: 7)
            
        Returns:
            Dict contenant le profil, santé, préférences et historique de repas
        """
        # Récupérer l'utilisateur par user_id (string)
        logger.info(f"Searching user with user_id={user_id}")
        user = await self.users_collection.find_one({"user_id": user_id})
        
        if not user:
            logger.warning(f"Utilisateur non trouvé: {user_id}")
            return {"error": f"User not found: {user_id}"}
        
        # Calculer la date de début pour l'historique
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.isoformat()
        
        # Récupérer les repas récents (async)
        # Utiliser le user_id (string) pour chercher dans meals
        logger.info(f"Searching meals for userId: {user_id}")
        
        # Chercher avec userId (string) - format standard dans la collection meals
        recent_meals_cursor = self.meals_collection.find({
            "userId": user_id,
            "dateScanned": {"$gte": start_date_str}
        }).sort("dateScanned", -1)
        recent_meals = await recent_meals_cursor.to_list(length=None)
        
        logger.info(f"Retrieved {len(recent_meals)} meals for user {user_id}")
        
        # Support des deux structures MongoDB (ancienne et nouvelle)
        profile = user.get("profile", user.get("profil", {}))
        medical = user.get("medical", {})
        nutrition = user.get("nutrition", user.get("alimentaire", {}))
        goals = user.get("goals", user.get("objectifs", {}))
        religious = user.get("religiousRestrictions", user.get("obligations_religieuses", {}))
        misc = user.get("misc", user.get("divers", {}))
        
        # Construire le contexte structuré
        context = {
            "user_profile": {
                # Support des deux formats de champs
                "age": profile.get("age"),
                "weight_kg": profile.get("weight", profile.get("poids")),
                "height_cm": profile.get("height", profile.get("taille")),
                "body_type": profile.get("bodyType", profile.get("morphologie", "")),
                "gender": profile.get("gender", profile.get("sexe", "")),
                "activity_level": misc.get("activityLevel", misc.get("niveau_activite", "")),
                "sports": misc.get("sports", []),
                "occupation": misc.get("occupation", misc.get("profession", ""))
            },
            "health_info": {
                "allergies": medical.get("allergies", []),
                "treatments": medical.get("treatments", medical.get("traitement", [])),
                "medical_history": medical.get("medicalHistory", medical.get("antecedents", {})),
                "birth_control": medical.get("birthControl", medical.get("pilule", {}))
            },
            "nutrition_preferences": {
                "diet": nutrition.get("diet", nutrition.get("regime", "")),
                "intolerances": nutrition.get("intolerances", []),
                "preferences": nutrition.get("preferences", []),
                "religious_restrictions": {
                    "practicing": religious.get("practicing", religious.get("pratique", False)),
                    "type": religious.get("type", "")
                }
            },
            "goals": {
                "muscle_gain": goals.get("muscleGain", goals.get("masse_musculaire", False)),
                "weight_loss": goals.get("weightLoss", goals.get("perte_de_poids", False)),
                "goal_detail": goals.get("goalDetail", goals.get("objectif_detail", "")),
                "performance": goals.get("performance", False),
                "maintain_shape": goals.get("maintainShape", False)
            },
            "meal_history": {
                "period": f"last_{days}_days",
                "start_date": start_date_str,
                "end_date": datetime.now().isoformat(),
                "total_meals": len(recent_meals),
                "meals": []
            },
            "period_statistics": {}
        }
        
        # Calculer les statistiques nutritionnelles
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        for meal in recent_meals:
            meal_data = {
                "name": meal.get("name", ""),
                "date": meal.get("dateScanned", ""),
                "ingredients": meal.get("ingredients", []),
                "nutrients": {
                    "calories": meal.get("nutrients", {}).get("calories", 0),
                    "protein": meal.get("nutrients", {}).get("protein", 0),
                    "carbohydrates": meal.get("nutrients", {}).get("carbohydrates", 0),
                    "fat": meal.get("nutrients", {}).get("fat", 0),
                    "fiber": meal.get("nutrients", {}).get("fiber", 0)
                }
            }
            context["meal_history"]["meals"].append(meal_data)
            
            # Accumuler les totaux
            nutrients = meal.get("nutrients", {})
            total_calories += nutrients.get("calories", 0)
            total_protein += nutrients.get("protein", 0)
            total_carbs += nutrients.get("carbohydrates", 0)
            total_fat += nutrients.get("fat", 0)
            total_fiber += nutrients.get("fiber", 0)
        
        # Statistiques de la période
        meal_count = len(recent_meals)
        if meal_count > 0:
            context["period_statistics"] = {
                "total_meals": meal_count,
                "totals": {
                    "calories": round(total_calories, 1),
                    "protein": round(total_protein, 1),
                    "carbohydrates": round(total_carbs, 1),
                    "fat": round(total_fat, 1),
                    "fiber": round(total_fiber, 1)
                }
            }
        
        context["generated_at"] = datetime.now().isoformat()
        return context
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Construit le prompt pour Gemini basé sur le contexte utilisateur.
        
        Args:
            context: Dictionnaire avec les données utilisateur
            
        Returns:
            Prompt formaté pour le LLM
        """
        profile = context.get("user_profile", {})
        health = context.get("health_info", {})
        nutrition = context.get("nutrition_preferences", {})
        goals = context.get("goals", {})
        meal_history = context.get("meal_history", {})
        stats = context.get("period_statistics", {})

        # Build an English prompt tailored to return a single concise suggestion
        prompt = f"""You are an expert nutritionist and health coach. Your task is to provide EXACTLY ONE concise meal suggestion for the NEXT meal of this user, using the context below.

USER CONTEXT:

- Age: {profile.get('age')}
- Gender: {profile.get('gender')}
- Weight (kg): {profile.get('weight_kg')}
- Height (cm): {profile.get('height_cm')}
- Body type: {profile.get('body_type')}
- Activity level: {profile.get('activity_level')}
- Sports: {', '.join(profile.get('sports') or []) or 'None'}
- Occupation: {profile.get('occupation')}

GOALS:
"""

        # Goals (converted to English labels)
        goal_items = []
        if goals.get('muscle_gain'):
            goal_items.append("- Muscle gain")
        if goals.get('weight_loss'):
            goal_items.append("- Weight loss")
        if goals.get('performance'):
            goal_items.append("- Performance improvement")
        if goals.get('maintain_shape'):
            goal_items.append("- Maintain fitness")
        if goals.get('goal_detail'):
            goal_items.append(f"- Detail: {goals['goal_detail']}")

        prompt += '\n'.join(goal_items) if goal_items else "Maintain general fitness"
        prompt += "\n\n"

        # Medical information
        prompt += "MEDICAL INFORMATION:\n"
        if health.get('allergies'):
            prompt += f"- Allergies: {', '.join(health['allergies'])}\n"
        if health.get('treatments'):
            treatments_str = []
            for treatment in health.get('treatments', []):
                if isinstance(treatment, dict):
                    treatment_name = treatment.get('name', treatment.get('nom', ''))
                    treatment_condition = treatment.get('condition', treatment.get('indication', ''))
                    treatments_str.append(f"{treatment_name} ({treatment_condition})")
                else:
                    treatments_str.append(str(treatment))
            if treatments_str:
                prompt += f"- Treatments: {', '.join(treatments_str)}\n"
        if health.get('medical_history'):
            history = health['medical_history']
            personal = history.get('personal', history.get('personnels', []))
            if personal:
                prompt += f"- Medical history: {', '.join(personal)}\n"
        if not health.get('allergies') and not health.get('treatments'):
            prompt += "- No specific medical constraints\n"
        prompt += "\n"

        # Nutrition preferences
        prompt += "NUTRITION PREFERENCES:\n"
        if nutrition.get('diet'):
            prompt += f"- Diet: {nutrition['diet']}\n"
        if nutrition.get('intolerances'):
            prompt += f"- Intolerances: {', '.join(nutrition['intolerances'])}\n"
        if nutrition.get('preferences'):
            prompt += f"- Preferences: {', '.join(nutrition['preferences'])}\n"
        religious = nutrition.get('religious_restrictions', {})
        if religious.get('practicing'):
            prompt += f"- Religious restriction: {religious.get('type')}\n"
        prompt += "\n"

        # Recent meal history
        prompt += "HISTORY (last 7 days):\n"
        if stats and stats.get('total_meals', 0) > 0:
            totals = stats.get('totals', {})
            prompt += f"- Recorded meals: {stats['total_meals']}\n"
            prompt += f"- Total calories: {totals.get('calories', 0):.0f} kcal\n"
            prompt += f"- Total protein: {totals.get('protein', 0):.1f} g\n"
            prompt += f"- Total carbohydrates: {totals.get('carbohydrates', 0):.1f} g\n"
            prompt += f"- Total fat: {totals.get('fat', 0):.1f} g\n"
            prompt += "\n"

            meals = meal_history.get('meals', [])
            if meals:
                prompt += "Recent meals:\n"
                for i, meal in enumerate(meals[:5], 1):
                    prompt += f"{i}. {meal.get('name')} - {meal.get('date')[:10]}\n"
                    nutrients = meal.get('nutrients', {})
                    prompt += f"   Nutrition: {nutrients.get('calories')} kcal | P:{nutrients.get('protein')}g | C:{nutrients.get('carbohydrates')}g | F:{nutrients.get('fat')}g\n"
                prompt += "\n"
        else:
            prompt += "- No meals recorded recently\n\n"

        # Instructions for the LLM: concise English output
        prompt += """
YOUR TASK:

Provide EXACTLY ONE concise meal suggestion for the NEXT meal of this user.

REQUIREMENTS:
- Output must be in English.
- Return exactly one single-line suggestion in PLAIN TEXT (no markdown, no emojis).
- Do NOT include recipes, preparation steps, ingredient lists, shopping lists, or multiple suggestions.
- Keep it very concise: maximum 2 short sentences.
- Start with the meal name followed by a colon and a brief description. Example:
  Grilled Salmon Bowl: Light grilled salmon with quinoa and greens — ~550 kcal, high protein.

Return only that single line and nothing else.
"""

        return prompt
    
    async def generate_suggestions(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Génère des suggestions de repas personnalisées via Gemini.
        
        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours d'historique à considérer
            
        Returns:
            Dict contenant les suggestions et le contexte utilisé
        """
        try:
            logger.info(f"Generating suggestion for user {user_id}")
            
            # Récupérer le contexte utilisateur (async)
            context = await self.get_user_context(user_id, days)
            
            if "error" in context:
                return {
                    "success": False,
                    "error": context["error"],
                    "generated_at": datetime.now().isoformat()
                }
            
            # Construire le prompt
            prompt = self.build_prompt(context)
            
            # Call Gemini
            logger.info(f"Calling Gemini ({self.model_name})...")
            response = self.model.generate_content(prompt)

            raw_text = getattr(response, 'text', str(response))
            # Extract the first non-empty line as the concise suggestion
            first_line = ""
            for line in raw_text.splitlines():
                if line.strip():
                    first_line = line.strip()
                    break

            logger.info("Suggestion generated successfully")

            return {
                "success": True,
                "suggestion": first_line,
                "raw": raw_text,
                "user_context": {
                    "user_id": str(user_id),
                    "profile": context["user_profile"],
                    "goals": context["goals"],
                    "period_statistics": context.get("period_statistics", {})
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error generating suggestion: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
