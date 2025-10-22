"""
Agent Médical - Analyse des conditions physiques, traitements et antécédents.

Cet agent analyse les informations médicales de l'utilisateur et fournit
un contexte médical à l'orchestrateur pour adapter les recommandations
alimentaires et sportives en fonction de l'état de santé.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
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


class MedicalAgent:
    """
    Agent médical qui analyse les conditions physiques, traitements médicaux
    et antécédents de l'utilisateur pour fournir un contexte médical pertinent
    aux autres agents (nutrition, coach, orchestrateur).
    """
    
    def __init__(
        self,
        mongo_db,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        load_env: bool = True
    ):
        """
        Initialise l'agent médical.
        
        Args:
            mongo_db: Instance de la base MongoDB (Motor async)
            api_key: Clé API Google Gemini
            model_name: Nom du modèle Gemini
            load_env: Si True, charge les variables d'environnement
        """
        self.db = mongo_db
        self.users_collection = mongo_db.user  # Collection 'user' au singulier
        
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
        
        logger.info(f"MedicalAgent initialisé avec le modèle {model_name}")
    
    async def get_user_medical_context(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le contexte médical complet d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant profil, antécédents, traitements et conditions
        """
        # Convertir en ObjectId
        if isinstance(user_id, str):
            try:
                user_oid = ObjectId(user_id)
            except Exception:
                user_oid = user_id
        else:
            user_oid = user_id
        
        # Récupérer l'utilisateur
        user = await self.users_collection.find_one({"_id": user_oid})
        
        if not user:
            logger.warning(f"Utilisateur non trouvé: {user_id}")
            return {"error": f"User not found: {user_id}"}
        
        # Extraire les données médicales (support des deux formats)
        profile = user.get("profile", user.get("profil", {}))
        medical = user.get("medical", {})
        nutrition = user.get("nutrition", user.get("alimentaire", {}))
        goals = user.get("goals", user.get("objectifs", {}))
        misc = user.get("misc", user.get("divers", {}))
        
        # Construire le contexte médical complet
        context = {
            "user_profile": {
                "age": profile.get("age"),
                "weight_kg": profile.get("weight", profile.get("poids")),
                "height_cm": profile.get("height", profile.get("taille")),
                "body_type": profile.get("bodyType", profile.get("morphologie", "")),
                "gender": profile.get("gender", profile.get("sexe", "")),
                "activity_level": misc.get("activityLevel", misc.get("niveau_activite", ""))
            },
            "medical_info": {
                "treatments": [],
                "allergies": medical.get("allergies", []),
                "medical_history": {
                    "personal": medical.get("medicalHistory", {}).get("personal", 
                                medical.get("medicalHistory", {}).get("personnels", [])),
                    "family": medical.get("medicalHistory", {}).get("family", 
                             medical.get("medicalHistory", {}).get("familiaux", []))
                },
                "birth_control": medical.get("birthControl", medical.get("pilule", {})),
                "injuries": medical.get("injuries", [])
            },
            "nutrition_constraints": {
                "diet": nutrition.get("diet", nutrition.get("regime", "")),
                "intolerances": nutrition.get("intolerances", []),
                "allergies": medical.get("allergies", [])
            },
            "health_goals": {
                "main_goal": goals.get("mainGoal", goals.get("objectif_principal", "")),
                "target_weight": goals.get("targetWeight", goals.get("poids_cible")),
                "muscle_gain": goals.get("muscleGain", goals.get("masse_musculaire", False)),
                "weight_loss": goals.get("weightLoss", goals.get("perte_de_poids", False)),
                "performance": goals.get("performance", False)
            }
        }
        
        # Formater les traitements
        for treatment in medical.get("treatments", medical.get("traitement", [])):
            if isinstance(treatment, dict):
                context["medical_info"]["treatments"].append({
                    "name": treatment.get("name", treatment.get("nom", "")),
                    "dosage": treatment.get("dosage", ""),
                    "condition": treatment.get("condition", treatment.get("indication", ""))
                })
            else:
                context["medical_info"]["treatments"].append({
                    "name": str(treatment),
                    "dosage": "",
                    "condition": ""
                })
        
        return context
    
    def build_medical_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """
        Construit le prompt pour analyser le contexte médical.
        
        Args:
            context: Contexte médical de l'utilisateur
            
        Returns:
            Prompt formaté pour Gemini
        """
        profile = context["user_profile"]
        medical = context["medical_info"]
        nutrition = context["nutrition_constraints"]
        goals = context["health_goals"]
        
        prompt = f"""You are an expert medical advisor specializing in personalized health recommendations for nutrition and fitness programs.

USER PROFILE:
- Age: {profile['age']} years old
- Gender: {profile['gender']}
- Weight: {profile['weight_kg']} kg
- Height: {profile['height_cm']} cm
- Body Type: {profile['body_type']}
- Activity Level: {profile['activity_level']}

MEDICAL INFORMATION:
"""
        
        # Traitements actuels
        if medical["treatments"]:
            prompt += "Current Treatments:\n"
            for treatment in medical["treatments"]:
                prompt += f"  - {treatment['name']}"
                if treatment['dosage']:
                    prompt += f" ({treatment['dosage']})"
                if treatment['condition']:
                    prompt += f" for {treatment['condition']}"
                prompt += "\n"
        else:
            prompt += "Current Treatments: None\n"
        
        # Allergies
        if medical["allergies"]:
            prompt += f"Allergies: {', '.join(medical['allergies'])}\n"
        else:
            prompt += "Allergies: None\n"
        
        # Antécédents personnels
        if medical["medical_history"]["personal"]:
            prompt += f"Personal Medical History: {', '.join(medical['medical_history']['personal'])}\n"
        else:
            prompt += "Personal Medical History: None reported\n"
        
        # Antécédents familiaux
        if medical["medical_history"]["family"]:
            prompt += f"Family Medical History: {', '.join(medical['medical_history']['family'])}\n"
        
        # Contraception
        birth_control = medical.get("birth_control", {})
        if isinstance(birth_control, dict) and birth_control.get("uses", birth_control.get("utilise", False)):
            bc_name = birth_control.get("name", birth_control.get("nom", "contraceptive"))
            prompt += f"Birth Control: {bc_name}\n"
        
        # Blessures
        if medical.get("injuries"):
            prompt += f"Current Injuries/Limitations: {', '.join(medical['injuries'])}\n"
        
        prompt += f"\nDIETARY CONSTRAINTS:\n"
        if nutrition["diet"]:
            prompt += f"- Diet Type: {nutrition['diet']}\n"
        if nutrition["intolerances"]:
            prompt += f"- Food Intolerances: {', '.join(nutrition['intolerances'])}\n"
        
        prompt += f"""
HEALTH GOALS:
- Main Goal: {goals['main_goal']}
- Target Weight: {goals.get('target_weight', 'Not specified')} kg
- Muscle Gain: {"Yes" if goals['muscle_gain'] else "No"}
- Weight Loss: {"Yes" if goals['weight_loss'] else "No"}
- Performance Focus: {"Yes" if goals['performance'] else "No"}

TASK:
Provide a concise medical analysis (2-3 sentences maximum) focusing on:
1. Key health considerations for meal planning
2. Important precautions for physical exercise
3. Nutrient priorities based on treatments/conditions
4. Any specific contraindications or recommendations

Format your response as a single paragraph in plain text English, starting with "Medical Context:"

Example:
Medical Context: Patient on blood pressure medication should monitor sodium intake and avoid intense cardio without medical clearance. Prioritize potassium-rich foods and stay well-hydrated. Previous knee injury requires low-impact exercises; strength training is encouraged with proper form.

Now generate the medical analysis:"""
        
        return prompt
    
    async def analyze_medical_context(self, user_id: str) -> Dict[str, Any]:
        """
        Analyse le contexte médical complet de l'utilisateur via Gemini.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict contenant l'analyse médicale et les recommandations
        """
        try:
            logger.info(f"Analyzing medical context for user {user_id}")
            
            # Récupérer le contexte médical
            context = await self.get_user_medical_context(user_id)
            
            if "error" in context:
                return {
                    "success": False,
                    "error": context["error"],
                    "generated_at": datetime.now().isoformat()
                }
            
            # Construire le prompt
            prompt = self.build_medical_analysis_prompt(context)
            
            # Appeler Gemini
            logger.info(f"Calling Gemini ({self.model_name}) for medical analysis...")
            response = self.model.generate_content(prompt)
            
            raw_text = getattr(response, 'text', str(response))
            
            # Extraire l'analyse médicale
            medical_analysis = ""
            for line in raw_text.splitlines():
                if line.strip():
                    medical_analysis = line.strip()
                    break
            
            logger.info("Medical analysis generated successfully")
            
            return {
                "success": True,
                "medical_analysis": medical_analysis,
                "raw": raw_text,
                "user_context": {
                    "user_id": str(user_id),
                    "profile": context["user_profile"],
                    "medical_info": context["medical_info"],
                    "nutrition_constraints": context["nutrition_constraints"],
                    "health_goals": context["health_goals"]
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing medical context: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Error analyzing medical context: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
    
    def get_medical_summary(self, context: Dict[str, Any]) -> str:
        """
        Génère un résumé texte du contexte médical pour les autres agents.
        
        Args:
            context: Contexte médical récupéré
            
        Returns:
            Résumé texte du contexte médical
        """
        medical = context.get("medical_info", {})
        
        summary_parts = []
        
        # Traitements
        treatments = medical.get("treatments", [])
        if treatments:
            treatment_names = [t.get("name", "") for t in treatments if t.get("name")]
            summary_parts.append(f"Treatments: {', '.join(treatment_names)}")
        
        # Allergies
        allergies = medical.get("allergies", [])
        if allergies:
            summary_parts.append(f"Allergies: {', '.join(allergies)}")
        
        # Antécédents
        personal_history = medical.get("medical_history", {}).get("personal", [])
        if personal_history:
            summary_parts.append(f"Medical History: {', '.join(personal_history)}")
        
        # Blessures
        injuries = medical.get("injuries", [])
        if injuries:
            summary_parts.append(f"Injuries: {', '.join(injuries)}")
        
        if not summary_parts:
            return "No significant medical constraints"
        
        return " | ".join(summary_parts)
