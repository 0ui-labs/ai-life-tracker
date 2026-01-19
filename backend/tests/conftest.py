"""Shared test fixtures for the backend test suite."""

import pytest
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

from app.services.context import ContextEngine


# =============================================================================
# Context Engine Fixtures
# =============================================================================

@pytest.fixture
def context_engine() -> ContextEngine:
    """Fresh ContextEngine instance for each test."""
    return ContextEngine()


@pytest.fixture
def user_id() -> str:
    """Standard test user ID."""
    return "test-user-123"


@pytest.fixture
def user_with_active_workout(context_engine: ContextEngine, user_id: str) -> str:
    """User ID with an active workout session started."""
    context_engine.start_workout(
        user_id=user_id,
        routine_name="Test Workout",
        exercises=[
            {"name": "Bankdrücken", "sets": 3, "reps": 10},
            {"name": "Rudern", "sets": 3, "reps": 10},
        ],
    )
    return user_id


# =============================================================================
# Database Fixtures (for integration tests)
# =============================================================================

@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock async database session for unit tests."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


# =============================================================================
# Time Fixtures
# =============================================================================

@pytest.fixture
def fixed_datetime() -> datetime:
    """Fixed datetime for deterministic tests."""
    return datetime(2024, 1, 15, 10, 30, 0)
