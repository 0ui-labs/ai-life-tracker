"""Tests for the ContextEngine - Workout session management."""

import pytest
from datetime import datetime
from unittest.mock import patch

from app.services.context import ContextEngine


class TestWorkoutLifecycle:
    """Tests for starting and ending workout sessions."""

    def test_new_user_has_no_active_workout(self, context_engine: ContextEngine, user_id: str):
        """A new user should not have an active workout by default."""
        ctx = context_engine.get_context(user_id)
        
        assert ctx["workout_active"] is False

    def test_start_workout_activates_session(self, context_engine: ContextEngine, user_id: str):
        """Starting a workout should mark the session as active."""
        context_engine.start_workout(user_id, routine_name="Push Day")
        
        ctx = context_engine.get_context(user_id)
        assert ctx["workout_active"] is True
        assert ctx["current_routine"] == "Push Day"

    def test_start_workout_initializes_set_counter_to_one(
        self, context_engine: ContextEngine, user_id: str
    ):
        """The set counter should start at 1 when workout begins."""
        context_engine.start_workout(user_id)
        
        ctx = context_engine.get_context(user_id)
        assert ctx["current_set"] == 1

    def test_end_workout_deactivates_session(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Ending a workout should deactivate the session."""
        context_engine.end_workout(user_with_active_workout)
        
        ctx = context_engine.get_context(user_with_active_workout)
        assert ctx["workout_active"] is False

    def test_end_workout_returns_summary_with_completed_exercises(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Ending a workout should return a summary of completed exercises."""
        summary = context_engine.end_workout(user_with_active_workout)
        
        assert "exercises_completed" in summary
        assert "completed_exercises" in summary
        assert "duration" in summary

    def test_end_workout_without_start_returns_empty_summary(
        self, context_engine: ContextEngine, user_id: str
    ):
        """Ending a workout that was never started should return safe defaults."""
        summary = context_engine.end_workout(user_id)
        
        assert summary["duration"] is None
        assert summary["exercises_completed"] == 0


class TestExerciseNavigation:
    """Tests for navigating through exercises in a workout."""

    def test_get_current_exercise_returns_first_planned_exercise(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Should return the first exercise when workout starts."""
        exercise = context_engine.get_current_exercise(user_with_active_workout)
        
        assert exercise is not None
        assert exercise["name"] == "Bankdrücken"

    def test_get_current_exercise_returns_none_when_no_workout(
        self, context_engine: ContextEngine, user_id: str
    ):
        """Should return None if no workout is active."""
        exercise = context_engine.get_current_exercise(user_id)
        
        assert exercise is None

    def test_next_exercise_advances_to_second_exercise(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Moving to next exercise should advance the index."""
        context_engine.next_exercise(user_with_active_workout)
        
        exercise = context_engine.get_current_exercise(user_with_active_workout)
        assert exercise is not None
        assert exercise["name"] == "Rudern"

    def test_next_exercise_adds_previous_to_completed_list(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Moving to next should mark previous exercise as completed."""
        context_engine.next_exercise(user_with_active_workout)
        
        ctx = context_engine.get_context(user_with_active_workout)
        assert len(ctx["completed_exercises"]) == 1
        assert ctx["completed_exercises"][0]["name"] == "Bankdrücken"


class TestSetRecording:
    """Tests for recording individual sets during a workout."""

    def test_record_set_increments_set_counter(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Recording a set should increment the set counter."""
        context_engine.record_set(user_with_active_workout, weight=80, reps=10)
        
        ctx = context_engine.get_context(user_with_active_workout)
        assert ctx["current_set"] == 2

    def test_record_set_stores_last_weight(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Recording a set should remember the weight for minimal input."""
        context_engine.record_set(user_with_active_workout, weight=80, reps=10)
        
        ctx = context_engine.get_context(user_with_active_workout)
        assert ctx["last_weight"] == 80

    def test_multiple_sets_increment_counter_correctly(
        self, context_engine: ContextEngine, user_with_active_workout: str
    ):
        """Multiple sets should increment the counter each time."""
        context_engine.record_set(user_with_active_workout, weight=80, reps=10)
        context_engine.record_set(user_with_active_workout, weight=80, reps=8)
        context_engine.record_set(user_with_active_workout, weight=80, reps=6)
        
        ctx = context_engine.get_context(user_with_active_workout)
        assert ctx["current_set"] == 4


class TestDurationCalculation:
    """Tests for workout duration calculation."""

    def test_calculate_duration_returns_none_for_none_input(
        self, context_engine: ContextEngine
    ):
        """Should handle None start time gracefully."""
        duration = context_engine._calculate_duration(None)
        
        assert duration is None

    def test_calculate_duration_returns_minutes(self, context_engine: ContextEngine):
        """Should calculate duration in minutes."""
        # Started 45 minutes ago
        with patch("app.services.context.datetime") as mock_dt:
            mock_dt.utcnow.return_value = datetime(2024, 1, 15, 11, 15, 0)
            mock_dt.fromisoformat = datetime.fromisoformat
            
            duration = context_engine._calculate_duration("2024-01-15T10:30:00")
            
            assert duration == 45
