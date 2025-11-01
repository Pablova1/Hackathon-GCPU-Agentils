"""
ADK Configuration Module

Centralizes all configuration for Google ADK agents.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types


class ADKConfig:
    """Configuration for ADK agents."""
    
    def __init__(self, load_env: bool = True):
        """Initialize ADK configuration."""
        if load_env:
            env_path = Path(__file__).parent.parent.parent.parent / ".env"
            load_dotenv(dotenv_path=env_path)
        
        self.api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in .env")
        
        # Configure the Google GenAI client
        self.client = genai.Client(api_key=self.api_key)
        
        self.default_model = "gemini-2.5-flash"
        
        # Agent configurations
        self.meal_agent_config = {
            "model": self.default_model,
            "temperature": 0.7,
            "max_output_tokens": 2048,
        }
        
        self.coach_agent_config = {
            "model": self.default_model,
            "temperature": 0.7,
            "max_output_tokens": 2048,
        }
        
        self.medical_agent_config = {
            "model": self.default_model,
            "temperature": 0.5,  
            "max_output_tokens": 2048,
        }
        
        self.orchestrator_config = {
            "model": self.default_model,
            "temperature": 0.8,
            "max_output_tokens": 4096,
        }


# Global config instance
_config_instance = None


def get_config() -> ADKConfig:
    """Get or create the global ADK config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ADKConfig()
    return _config_instance
