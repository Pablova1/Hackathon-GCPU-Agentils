"""
Test script to verify OnboardingAgent loads environment variables correctly
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai.agents.agent_onboarding.agent import OnboardingAgent

print("=" * 60)
print("Testing OnboardingAgent initialization")
print("=" * 60)

try:
    agent = OnboardingAgent(load_env=True)
    print("\n✅ Agent initialized successfully!")
    print(f"   - API Key loaded: {bool(agent.api_key)}")
    print(f"   - Project ID: {agent.project_id}")
    print(f"   - Region: {agent.region}")
    print(f"   - System Prompt loaded: {bool(agent.system_prompt)}")
    print(f"   - System Prompt preview: {agent.system_prompt[:150]}...")
    print(f"   - Max questions: {agent.max_questions}")
    
except Exception as e:
    print(f"\n❌ Error initializing agent: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
