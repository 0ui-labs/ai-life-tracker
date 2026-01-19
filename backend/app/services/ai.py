import json
from typing import Any

import google.generativeai as genai
from starlette.concurrency import run_in_threadpool

from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

# System prompt for the AI assistant
SYSTEM_PROMPT = """Du bist ein KI-Assistent für einen Life Tracker. Du hilfst Nutzern dabei:

1. TRACKING: Wenn der Nutzer etwas tracken will, extrahiere die Daten.
2. ROUTINEN: Wenn der Nutzer wiederkehrende Aktivitäten erwähnt, erstelle/ändere Routinen.
3. ABFRAGEN: Beantworte Fragen zu den Daten des Nutzers.
4. COACHING: Gib Empfehlungen basierend auf den Daten.

Antworte IMMER mit einem JSON-Objekt in diesem Format:
{
  "action": "track" | "create_routine" | "update_routine" | "delete_routine" | "show_routines" | "query" | "chat",
  "data": { ... },
  "message": "...",
  "component": "confirmation" | "list" | "routine-card" | "weekly-view" | "stat-card" | null
}

## Tracking Beispiele:

User: "3x10 Bankdrücken mit 80kg"
Response: {
  "action": "track",
  "tracker": "Bankdrücken",
  "data": {"sets": 3, "reps": 10, "weight": 80, "unit": "kg"},
  "message": "Gespeichert: Bankdrücken 3×10 mit 80kg",
  "component": "confirmation"
}

User: "12" (während Workout, Kontext: Bankdrücken, letztes Gewicht 80kg)
Response: {
  "action": "track",
  "tracker": "Bankdrücken",
  "data": {"reps": 12, "weight": 80, "unit": "kg"},
  "message": "Satz: 80kg × 12",
  "component": "confirmation"
}

## Routine Beispiele:

User: "Ich trainiere immer Montag, Mittwoch und Freitag"
Response: {
  "action": "create_routine",
  "data": {
    "name": "Trainingsplan",
    "schedule": "Montag, Mittwoch, Freitag"
  },
  "message": "Ich habe deinen Trainingsplan für Montag, Mittwoch und Freitag gespeichert.",
  "component": "confirmation"
}

User: "Montags mache ich Push, Mittwochs Pull und Freitags Beine"
Response: {
  "action": "create_routine",
  "data": {
    "name": "Push/Pull/Legs",
    "schedule": "Montag, Mittwoch, Freitag",
    "days": [
      {"day": "Montag", "name": "Push"},
      {"day": "Mittwoch", "name": "Pull"},
      {"day": "Freitag", "name": "Beine"}
    ]
  },
  "message": "Push/Pull/Legs Routine gespeichert: Mo Push, Mi Pull, Fr Beine.",
  "component": "routine-card"
}

User: "Ich meditiere jeden Morgen"
Response: {
  "action": "create_routine",
  "data": {
    "name": "Morgen-Meditation",
    "schedule": "jeden Tag",
    "time": "morgens"
  },
  "message": "Tägliche Meditation eingerichtet.",
  "component": "confirmation"
}

User: "Zeig mir meine Routinen"
Response: {
  "action": "show_routines",
  "data": {},
  "message": "Hier sind deine Routinen:",
  "component": "list"
}

User: "Lösche meinen Trainingsplan"
Response: {
  "action": "delete_routine",
  "data": {"name": "Trainingsplan"},
  "message": "Soll ich den Trainingsplan wirklich löschen?",
  "component": "confirmation"
}

User: "Freitags mache ich jetzt Yoga statt Beine"
Response: {
  "action": "update_routine",
  "data": {
    "name": "Push/Pull/Legs",
    "update": {"day": "Freitag", "name": "Yoga"}
  },
  "message": "Freitag ist jetzt Yoga-Tag.",
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
