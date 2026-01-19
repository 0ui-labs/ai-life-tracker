from typing import Any
from datetime import datetime, date


class ContextEngine:
    """Manages conversation and workout context for smart AI interactions."""
    
    def __init__(self):
        # In production, this would be stored in Redis or similar
        self._contexts: dict[str, dict[str, Any]] = {}
    
    def get_context(self, user_id: str) -> dict[str, Any]:
        """Get current context for a user."""
        if user_id not in self._contexts:
            self._contexts[user_id] = self._default_context()
        return self._contexts[user_id]
    
    def update_context(self, user_id: str, updates: dict[str, Any]) -> None:
        """Update context for a user."""
        ctx = self.get_context(user_id)
        ctx.update(updates)
        ctx["last_updated"] = datetime.utcnow().isoformat()
    
    def start_workout(
        self,
        user_id: str,
        routine_name: str | None = None,
        exercises: list[dict] | None = None,
    ) -> None:
        """Start a workout session."""
        self.update_context(user_id, {
            "workout_active": True,
            "workout_started": datetime.utcnow().isoformat(),
            "current_routine": routine_name,
            "planned_exercises": exercises or [],
            "current_exercise_index": 0,
            "current_set": 1,
            "last_weight": None,
            "completed_exercises": [],
        })
    
    def end_workout(self, user_id: str) -> dict[str, Any]:
        """End workout and return summary."""
        ctx = self.get_context(user_id)
        summary = {
            "duration": self._calculate_duration(ctx.get("workout_started")),
            "exercises_completed": len(ctx.get("completed_exercises", [])),
            "completed_exercises": ctx.get("completed_exercises", []),
        }
        
        # Reset workout context
        self.update_context(user_id, {
            "workout_active": False,
            "workout_started": None,
            "current_routine": None,
            "planned_exercises": [],
            "current_exercise_index": 0,
            "current_set": 1,
            "last_weight": None,
            "completed_exercises": [],
        })
        
        return summary
    
    def get_current_exercise(self, user_id: str) -> dict[str, Any] | None:
        """Get current exercise in active workout."""
        ctx = self.get_context(user_id)
        if not ctx.get("workout_active"):
            return None
        
        exercises = ctx.get("planned_exercises", [])
        index = ctx.get("current_exercise_index", 0)
        
        if index < len(exercises):
            return exercises[index]
        return None
    
    def next_exercise(self, user_id: str) -> dict[str, Any] | None:
        """Move to next exercise."""
        ctx = self.get_context(user_id)
        current = self.get_current_exercise(user_id)
        
        if current:
            completed = ctx.get("completed_exercises", [])
            completed.append(current)
            self.update_context(user_id, {
                "completed_exercises": completed,
                "current_exercise_index": ctx.get("current_exercise_index", 0) + 1,
                "current_set": 1,
                "last_weight": None,
            })
        
        return self.get_current_exercise(user_id)
    
    def record_set(self, user_id: str, weight: float, reps: int) -> None:
        """Record a set and update context."""
        ctx = self.get_context(user_id)
        self.update_context(user_id, {
            "last_weight": weight,
            "current_set": ctx.get("current_set", 1) + 1,
        })
    
    def _default_context(self) -> dict[str, Any]:
        """Default context for new users."""
        return {
            "workout_active": False,
            "workout_started": None,
            "current_routine": None,
            "planned_exercises": [],
            "current_exercise_index": 0,
            "current_set": 1,
            "last_weight": None,
            "completed_exercises": [],
            "today": date.today().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def _calculate_duration(self, started: str | None) -> int | None:
        """Calculate workout duration in minutes."""
        if not started:
            return None
        start = datetime.fromisoformat(started)
        return int((datetime.utcnow() - start).total_seconds() / 60)


# Singleton instance
context_engine = ContextEngine()
