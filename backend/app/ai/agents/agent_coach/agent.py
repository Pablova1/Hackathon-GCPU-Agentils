"""
Agent Coach - Suggestions d'entraînement personnalisées.

Bonjour moi je suis coach.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from bson import ObjectId


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CoachAgent:
    """
    Agent qui génère des suggestions d'entraînement personnalisées
    basées sur le profil utilisateur, ses objectifs fitness et son historique sportif.
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
        Initialise l'agent coach.
        
        Args:
            mongo_db: Instance de la base MongoDB (Motor async)
            project_id: Google Cloud Project ID
            location: Google Cloud Location (e.g., 'us-central1')
            model_name: Nom du modèle Gemini
            load_env: Si True, charge les variables d'environnement
        """
        self.db = mongo_db
        self.users_collection = mongo_db.user  # Collection 'user' au singulier
        self.workouts_collection = mongo_db.workouts  # Collection des entraînements
        
        # Charger les variables d'environnement
        if load_env:
            env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY manquant dans .env")
        
        # Initialiser Gemini API
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"CoachAgent initialisé avec le modèle {model_name} via Gemini API")
    
    async def get_user_fitness_context(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Récupère le contexte fitness complet d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur (string format "user_xxxxx")
            days: Nombre de jours d'historique sportif à récupérer
            
        Returns:
            Dict contenant profil, objectifs, et historique d'entraînement
        """
        # Récupérer l'utilisateur par user_id (string) OU _id (ObjectId)
        logger.info(f"Searching user with user_id={user_id}")
        
        # Essayer d'abord avec user_id (string)
        user = await self.users_collection.find_one({"user_id": user_id})
        
        # Si pas trouvé, essayer avec _id (ObjectId)
        if not user:
            try:
                from bson import ObjectId
                user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            except:
                pass
        
        if not user:
            logger.warning(f"User not found with user_id={user_id}")
            return {"error": f"User not found: {user_id}"}
        
        # Récupérer le user_id (string) pour les requêtes suivantes
        actual_user_id = user.get("user_id", str(user.get("_id")))
        
        logger.info(f"User found: {user.get('profile', {}).get('firstName', 'Unknown')} {user.get('profile', {}).get('lastName', '')}")
        
        # Calculer la date de début pour l'historique
        start_date = datetime.now() - timedelta(days=days)
        start_date_str = start_date.isoformat()
        
        # Utiliser le user_id (string) pour chercher dans workouts
        logger.info(f"Searching workouts with userId='{actual_user_id}' (string)")
        
        # Chercher avec userId (camelCase, string) - format dans la collection workouts
        workouts_cursor = self.workouts_collection.find({
            "userId": actual_user_id,
            "date": {"$gte": start_date_str}
        }).sort("date", -1)
        recent_workouts = await workouts_cursor.to_list(length=None)
        
        logger.info(f"Retrieved {len(recent_workouts)} workouts for userId='{user_id}'")
        
        # Extraire les données du profil
        profile = user.get("profile", user.get("profil", {}))
        medical = user.get("medical", {})
        goals = user.get("goals", user.get("objectifs", {}))
        misc = user.get("misc", user.get("divers", {}))
        
        # Construire le contexte fitness
        context = {
            "user_profile": {
                "age": profile.get("age"),
                "weight_kg": profile.get("weight", profile.get("poids")),
                "height_cm": profile.get("height", profile.get("taille")),
                "body_type": profile.get("bodyType", profile.get("morphologie", "")),
                "gender": profile.get("gender", profile.get("sexe", "")),
                "activity_level": misc.get("activityLevel", misc.get("niveau_activite", "")),
                "current_sports": misc.get("sports", []),
                "occupation": misc.get("occupation", misc.get("profession", ""))
            },
            "fitness_goals": {
                "main_goal": goals.get("mainGoal", goals.get("objectif_principal", "")),
                "target_weight": goals.get("targetWeight", goals.get("poids_cible")),
                "weight_change_pace": goals.get("weightChangePace", goals.get("rythme", "")),
                "areas_to_improve": goals.get("areasToImprove", goals.get("zones_ameliorer", [])),
                "fitness_level": goals.get("fitnessLevel", "intermediate")
            },
            "health_constraints": {
                "injuries": medical.get("injuries", []),
                "medical_conditions": medical.get("medicalHistory", {}),
                "physical_limitations": medical.get("limitations", [])
            },
            "workout_history": self._analyze_workout_history(recent_workouts),
            "raw_workouts": recent_workouts[:5]  # Les 5 derniers entraînements
        }
        
        return context
    
    def _analyze_workout_history(self, workouts: list) -> Dict[str, Any]:
        """
        Analyse l'historique d'entraînement pour extraire des statistiques.
        
        Args:
            workouts: Liste des entraînements
            
        Returns:
            Dict avec statistiques (fréquence, types, intensité, etc.)
        """
        if not workouts:
            return {
                "total_workouts": 0,
                "frequency_per_week": 0,
                "workout_types": {},
                "average_duration_min": 0,
                "consistency": "low"
            }
        
        total = len(workouts)
        workout_types = {}
        total_duration = 0
        
        for workout in workouts:
            wtype = workout.get("type", "unknown")
            workout_types[wtype] = workout_types.get(wtype, 0) + 1
            total_duration += workout.get("duration_minutes", 0)
        
        avg_duration = total_duration / total if total > 0 else 0
        frequency = (total / 7) if len(workouts) > 0 else 0
        
        # Déterminer la consistance
        if frequency >= 4:
            consistency = "high"
        elif frequency >= 2:
            consistency = "medium"
        else:
            consistency = "low"
        
        return {
            "total_workouts": total,
            "frequency_per_week": round(frequency, 1),
            "workout_types": workout_types,
            "average_duration_min": round(avg_duration, 1),
            "consistency": consistency
        }
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Construit le prompt pour Gemini basé sur le contexte fitness.
        
        Args:
            context: Contexte utilisateur et historique
            
        Returns:
            Prompt formaté pour Gemini
        """
        profile = context["user_profile"]
        goals = context["fitness_goals"]
        health = context["health_constraints"]
        history = context["workout_history"]
        
        prompt = f"""You are an expert fitness coach and personal trainer with deep knowledge of exercise science, sports medicine, and training periodization.

USER PROFILE:
- Age: {profile['age']} years old
- Gender: {profile['gender']}
- Weight: {profile['weight_kg']} kg
- Height: {profile['height_cm']} cm
- Body Type: {profile['body_type']}
- Activity Level: {profile['activity_level']}
- Current Sports: {', '.join(profile['current_sports']) if profile['current_sports'] else 'None'}

FITNESS GOALS:
- Main Goal: {goals['main_goal']}
- Target Weight: {goals.get('target_weight', 'Not specified')} kg
- Fitness Level: {goals.get('fitness_level', 'intermediate')}
- Areas to Improve: {', '.join(goals.get('areas_to_improve', [])) if goals.get('areas_to_improve') else 'General fitness'}

HEALTH CONSTRAINTS:
- Injuries: {', '.join(health.get('injuries', [])) if health.get('injuries') else 'None'}
- Physical Limitations: {', '.join(health.get('physical_limitations', [])) if health.get('physical_limitations') else 'None'}

RECENT WORKOUT HISTORY ({history['total_workouts']} workouts in last 7 days):
- Frequency: {history['frequency_per_week']} workouts/week
- Average Duration: {history['average_duration_min']} minutes
- Workout Types: {', '.join([f"{k} ({v}x)" for k, v in history['workout_types'].items()]) if history['workout_types'] else 'No recent activity'}
- Consistency: {history['consistency']}

TASK:
Generate EXACTLY ONE concise workout suggestion in PLAIN TEXT English.

REQUIREMENTS:
1. One specific workout session adapted to their goals and current fitness level
2. Include: workout type, duration, intensity level
3. Consider their recent activity to avoid overtraining
4. Account for any injuries or limitations
5. Be motivating and realistic
6. Format: "Workout Type: Brief description — Duration, Intensity (e.g., ~45min, Moderate)"

OUTPUT FORMAT (ONE LINE):
[Workout Name]: [Brief description with key exercises] — ~[XX]min, [Intensity level]

EXAMPLE:
Upper Body Strength: 5x5 bench press, pull-ups, overhead press with progressive overload — ~50min, High intensity

Now generate the suggestion:"""
        
        return prompt
    
    async def generate_suggestions(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Génère une suggestion d'entraînement personnalisée via Gemini.
        
        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours d'historique à considérer
            
        Returns:
            Dict contenant la suggestion et le contexte utilisé
        """
        try:
            logger.info(f"Generating workout suggestion for user {user_id}")
            
            # Récupérer le contexte fitness
            context = await self.get_user_fitness_context(user_id, days)
            
            if "error" in context:
                return {
                    "success": False,
                    "error": context["error"],
                    "generated_at": datetime.now().isoformat()
                }
            
            # Construire le prompt
            prompt = self.build_prompt(context)
            
            # Appeler Gemini
            logger.info(f"Calling Gemini ({self.model_name}) for workout suggestion...")
            response = self.model.generate_content(prompt)
            
            raw_text = getattr(response, 'text', str(response))
            
            # Extraire la première ligne non-vide comme suggestion concise
            first_line = ""
            for line in raw_text.splitlines():
                if line.strip():
                    first_line = line.strip()
                    break
            
            logger.info("Workout suggestion generated successfully")
            
            return {
                "success": True,
                "suggestion": first_line,
                "raw": raw_text,
                "user_context": {
                    "user_id": str(user_id),
                    "profile": context["user_profile"],
                    "goals": context["fitness_goals"],
                    "workout_statistics": context.get("workout_history", {})
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating workout suggestion: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error generating workout suggestion: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
