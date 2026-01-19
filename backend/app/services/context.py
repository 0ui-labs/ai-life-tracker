import json
from datetime import date, datetime
from typing import Any

import redis.asyncio as redis

from app.config import settings


class ContextEngine:
    """Manages conversation and workout context for smart AI interactions.

    Uses Redis as a shared store to support multi-worker deployments.
    Contexts automatically expire after a configurable TTL.
    """

    CONTEXT_KEY_PREFIX = "context:"

    def __init__(self, redis_client: redis.Redis | None = None):  # type: ignore[type-arg]
        """Initialize the context engine.

        Args:
            redis_client: Optional async Redis client for dependency injection (testing).
                         If not provided, creates a client from settings.
        """
        if redis_client is not None:
            self._redis: redis.Redis = redis_client  # type: ignore[type-arg]
        else:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        self._ttl = settings.context_ttl_seconds

    def _key(self, user_id: str) -> str:
        """Generate Redis key for a user's context."""
        return f"{self.CONTEXT_KEY_PREFIX}{user_id}"

    async def get_context(self, user_id: str) -> dict[str, Any]:
        """Get current context for a user.

        If no context exists, creates and stores a default one.
        Refreshes TTL on each access.
        """
        key = self._key(user_id)
        data = await self._redis.get(key)

        if data is None:
            ctx = self._default_context()
            await self._save_context(user_id, ctx)
            return ctx

        # Refresh TTL on access
        await self._redis.expire(key, self._ttl)
        return json.loads(str(data))

    async def update_context(self, user_id: str, updates: dict[str, Any]) -> None:
        """Update context for a user."""
        ctx = await self.get_context(user_id)
        ctx.update(updates)
        ctx["last_updated"] = datetime.utcnow().isoformat()
        await self._save_context(user_id, ctx)

    async def _save_context(self, user_id: str, ctx: dict[str, Any]) -> None:
        """Save context to Redis with TTL."""
        key = self._key(user_id)
        await self._redis.setex(key, self._ttl, json.dumps(ctx))

    async def start_workout(
        self,
        user_id: str,
        routine_name: str | None = None,
        exercises: list[dict] | None = None,
    ) -> None:
        """Start a workout session."""
        await self.update_context(user_id, {
            "workout_active": True,
            "workout_started": datetime.utcnow().isoformat(),
            "current_routine": routine_name,
            "planned_exercises": exercises or [],
            "current_exercise_index": 0,
            "current_set": 1,
            "last_weight": None,
            "completed_exercises": [],
        })

    async def end_workout(self, user_id: str) -> dict[str, Any]:
        """End workout and return summary."""
        ctx = await self.get_context(user_id)
        summary = {
            "duration": self._calculate_duration(ctx.get("workout_started")),
            "exercises_completed": len(ctx.get("completed_exercises", [])),
            "completed_exercises": ctx.get("completed_exercises", []),
        }

        # Reset workout context
        await self.update_context(user_id, {
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

    async def get_current_exercise(self, user_id: str) -> dict[str, Any] | None:
        """Get current exercise in active workout."""
        ctx = await self.get_context(user_id)
        if not ctx.get("workout_active"):
            return None

        exercises = ctx.get("planned_exercises", [])
        index = ctx.get("current_exercise_index", 0)

        if index < len(exercises):
            return exercises[index]
        return None

    async def next_exercise(self, user_id: str) -> dict[str, Any] | None:
        """Move to next exercise."""
        ctx = await self.get_context(user_id)
        current = await self.get_current_exercise(user_id)

        if current:
            completed = ctx.get("completed_exercises", [])
            completed.append(current)
            await self.update_context(user_id, {
                "completed_exercises": completed,
                "current_exercise_index": ctx.get("current_exercise_index", 0) + 1,
                "current_set": 1,
                "last_weight": None,
            })

        return await self.get_current_exercise(user_id)

    async def record_set(self, user_id: str, weight: float, reps: int) -> None:
        """Record a set and update context."""
        ctx = await self.get_context(user_id)
        await self.update_context(user_id, {
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


# Singleton instance - uses Redis from settings
context_engine = ContextEngine()
