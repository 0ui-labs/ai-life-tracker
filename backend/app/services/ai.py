import json
from typing import Any
import google.generativeai as genai
from starlette.concurrency import run_in_threadpool

from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

# System prompt for the AI assistant
SYSTEM_PROMPT = """Du bist ein KI-Assistent für einen Life Tracker. Du hilfst Nutzern dabei:

1. TRACKING: Wenn der Nutzer etwas tracken will, extrahiere die Daten und gib sie als JSON zurück.
2. NEUER TRACKER: Wenn der Nutzer etwas Neues tracken will, frage nach dem Schema.
3. ABFRAGEN: Beantworte Fragen zu den Daten des Nutzers.
4. COACHING: Gib Empfehlungen basierend auf den Daten.

Für Tracking-Eingaben, antworte IMMER mit einem JSON-Objekt in diesem Format:
{
  "action": "track" | "create_tracker" | "query" | "chat",
  "data": { ... },  // Die extrahierten Daten
  "message": "..."  // Deine Antwort an den Nutzer
  "component": "confirmation" | "list" | "chart" | "stat-card" | null  // UI Komponente
}

Beispiel für Workout-Tracking:
User: "3x10 Bankdrücken mit 80kg"
Response: {
  "action": "track",
  "tracker": "Bankdrücken",
  "data": {"sets": 3, "reps": 10, "weight": 80, "unit": "kg"},
  "message": "Gespeichert: Bankdrücken 3×10 mit 80kg",
  "component": "confirmation"
}

Beispiel für minimale Eingabe während Workout (Kontext: Bankdrücken, letztes Gewicht 80kg):
User: "12"
Response: {
  "action": "track",
  "tracker": "Bankdrücken",
  "data": {"reps": 12, "weight": 80, "unit": "kg"},
  "message": "Satz: 80kg × 12",
  "component": "confirmation"
}

Sei kurz und präzise in deinen Antworten.
"""


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
    
    async def process_message(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a user message and return structured response."""
        
        # Build context string
        context_str = ""
        if context:
            context_str = f"\n\nAktueller Kontext:\n{json.dumps(context, ensure_ascii=False)}"
        
        prompt = f"{message}{context_str}"
        
        try:
            response = await run_in_threadpool(self.model.generate_content, prompt)
            text = response.text
            
            # Try to parse as JSON
            try:
                # Find JSON in response
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
            
            # Fallback: return as chat message
            return {
                "action": "chat",
                "message": text,
                "component": None,
            }
            
        except Exception as e:
            return {
                "action": "error",
                "message": f"AI Error: {str(e)}",
                "component": None,
            }


# Singleton instance
ai_service = AIService()
