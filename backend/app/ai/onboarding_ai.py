from dotenv import load_dotenv, find_dotenv
import os, requests

load_dotenv(find_dotenv())
API_KEY: str | None = os.getenv("API_KEY")
PROJECT_ID: str | None = os.getenv("PROJECT_ID")
REGION: str = os.getenv("REGION")
AI_SYSTEM_PROMPT = os.getenv("AI_SYSTEM_PROMPT")

def suggest_followup(slots: dict, asked_ai_count: int) -> dict | None:
    """Propose une question IA optionnelle, ou None si rien à dire."""
    if asked_ai_count >= 3:
        return None
    context_lines = [f"{k}: {v}" for k, v in slots.items() if v]
    context_text = "\n".join(context_lines) or "Aucun contexte fourni."
    prompt = f"""{AI_SYSTEM_PROMPT} 
            {context_text} 
            """

    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"[VertexAI] Erreur API: {e}")
        return None

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        print("[VertexAI] Format de réponse inattendu:", data)
        return None
    
    if text.upper().startswith("AUCUNE"):
        return None
    
    return {
        "slot": f"ai_followup_{asked_ai_count}",  # ← Slot unique pour chaque question IA
        "text": text,
        "type": "text",
        "source": "ai"
    }