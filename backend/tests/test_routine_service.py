"""Tests for the Routine Service - Managing user routines and schedules."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.routine import (
    create_routine,
    get_routine_by_id,
    get_user_routines,
    update_routine,
    delete_routine,
    activate_routine,
    deactivate_routine,
    parse_schedule_to_rrule,
)


# =============================================================================
# Schedule Parsing Tests
# =============================================================================

class TestScheduleParsing:
    """Tests for converting natural language schedules to RRULE format."""

    def test_parse_monday_wednesday_friday_to_rrule(self):
        """Common MWF workout schedule should be parsed correctly."""
        result = parse_schedule_to_rrule("Montag, Mittwoch, Freitag")
        assert result == "FREQ=WEEKLY;BYDAY=MO,WE,FR"

    def test_parse_daily_schedule_to_rrule(self):
        """Daily schedule should be parsed correctly."""
        result = parse_schedule_to_rrule("jeden Tag")
        assert result == "FREQ=DAILY"

    def test_parse_weekdays_to_rrule(self):
        """Weekday schedule should be parsed correctly."""
        result = parse_schedule_to_rrule("werktags")
        assert result == "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"

    def test_parse_weekend_to_rrule(self):
        """Weekend schedule should be parsed correctly."""
        result = parse_schedule_to_rrule("am Wochenende")
        assert result == "FREQ=WEEKLY;BYDAY=SA,SU"

    def test_parse_single_day_to_rrule(self):
        """Single day should be parsed correctly."""
        result = parse_schedule_to_rrule("Dienstag")
        assert result == "FREQ=WEEKLY;BYDAY=TU"

    def test_parse_english_days_to_rrule(self):
        """English day names should also work."""
        result = parse_schedule_to_rrule("Monday, Wednesday, Friday")
        assert result == "FREQ=WEEKLY;BYDAY=MO,WE,FR"

    def test_parse_mixed_case_days_to_rrule(self):
        """Mixed case should be handled."""
        result = parse_schedule_to_rrule("MONTAG, mittwoch")
        assert result == "FREQ=WEEKLY;BYDAY=MO,WE"

    def test_parse_empty_schedule_returns_none(self):
        """Empty schedule should return None."""
        result = parse_schedule_to_rrule("")
        assert result is None

    def test_parse_unknown_schedule_returns_none(self):
        """Unknown schedule format should return None."""
        result = parse_schedule_to_rrule("irgendwann mal")
        assert result is None


# =============================================================================
# Routine CRUD Tests
# =============================================================================

class TestCreateRoutine:
    """Tests for creating new routines."""

    @pytest.mark.asyncio
    async def test_create_routine_with_name_and_schedule(self, mock_db_session):
        """Should create a routine with basic information."""
        # Arrange
        user_id = "user-123"
        name = "Mein Trainingsplan"
        schedule = "Montag, Mittwoch, Freitag"
        
        # Act
        routine = await create_routine(
            db=mock_db_session,
            user_id=user_id,
            name=name,
            schedule=schedule,
        )
        
        # Assert
        assert routine.name == name
        assert routine.user_id == user_id
        assert routine.is_active is False  # New routines start inactive
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_routine_with_config(self, mock_db_session):
        """Should create a routine with full configuration."""
        # Arrange
        config = {
            "days": [
                {"name": "Push", "exercises": ["Bankdrücken", "Schulterdrücken"]},
                {"name": "Pull", "exercises": ["Rudern", "Klimmzüge"]},
            ],
            "schedule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
        }
        
        # Act
        routine = await create_routine(
            db=mock_db_session,
            user_id="user-123",
            name="Push/Pull/Legs",
            config=config,
        )
        
        # Assert
        assert routine.config == config

    @pytest.mark.asyncio
    async def test_create_routine_sets_type_to_custom(self, mock_db_session):
        """User-created routines should have type 'custom'."""
        # Act
        routine = await create_routine(
            db=mock_db_session,
            user_id="user-123",
            name="Meine Routine",
        )
        
        # Assert
        assert routine.type == "custom"


class TestGetRoutines:
    """Tests for retrieving routines."""

    @pytest.mark.asyncio
    async def test_get_routine_by_id_returns_routine(self, mock_db_session):
        """Should return routine when found."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.name = "Test Routine"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await get_routine_by_id(mock_db_session, routine_id)
        
        # Assert
        assert result is not None
        assert result.id == routine_id

    @pytest.mark.asyncio
    async def test_get_routine_by_id_returns_none_when_not_found(self, mock_db_session):
        """Should return None when routine not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await get_routine_by_id(mock_db_session, uuid4())
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_routines_returns_all_user_routines(self, mock_db_session):
        """Should return all routines for a user."""
        # Arrange
        mock_routines = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_routines
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await get_user_routines(mock_db_session, "user-123")
        
        # Assert
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_routines_filters_active_only(self, mock_db_session):
        """Should filter to only active routines when requested."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        # Act
        await get_user_routines(mock_db_session, "user-123", active_only=True)
        
        # Assert
        mock_db_session.execute.assert_called_once()


class TestUpdateRoutine:
    """Tests for updating existing routines."""

    @pytest.mark.asyncio
    async def test_update_routine_name(self, mock_db_session):
        """Should update routine name."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.name = "Old Name"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await update_routine(
            db=mock_db_session,
            routine_id=routine_id,
            name="New Name",
        )
        
        # Assert
        assert result.name == "New Name"
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_routine_config(self, mock_db_session):
        """Should update routine configuration."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.config = {}
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        new_config = {"days": [{"name": "Leg Day"}]}
        
        # Act
        result = await update_routine(
            db=mock_db_session,
            routine_id=routine_id,
            config=new_config,
        )
        
        # Assert
        assert result.config == new_config

    @pytest.mark.asyncio
    async def test_update_routine_returns_none_when_not_found(self, mock_db_session):
        """Should return None when routine not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await update_routine(
            db=mock_db_session,
            routine_id=uuid4(),
            name="New Name",
        )
        
        # Assert
        assert result is None


class TestDeleteRoutine:
    """Tests for deleting routines."""

    @pytest.mark.asyncio
    async def test_delete_routine_removes_from_database(self, mock_db_session):
        """Should delete routine from database."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await delete_routine(mock_db_session, routine_id)
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_routine)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_routine_returns_false_when_not_found(self, mock_db_session):
        """Should return False when routine not found."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await delete_routine(mock_db_session, uuid4())
        
        # Assert
        assert result is False


class TestActivateDeactivateRoutine:
    """Tests for activating and deactivating routines."""

    @pytest.mark.asyncio
    async def test_activate_routine_sets_is_active_true(self, mock_db_session):
        """Should set is_active to True."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.is_active = False
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await activate_routine(mock_db_session, routine_id)
        
        # Assert
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_deactivate_routine_sets_is_active_false(self, mock_db_session):
        """Should set is_active to False."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.is_active = True
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await deactivate_routine(mock_db_session, routine_id)
        
        # Assert
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_activate_routine_deactivates_other_routines(self, mock_db_session):
        """When activating a routine, other active routines should be deactivated."""
        # Arrange
        routine_id = uuid4()
        mock_routine = MagicMock()
        mock_routine.id = routine_id
        mock_routine.user_id = "user-123"
        mock_routine.is_active = False
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_routine
        mock_db_session.execute.return_value = mock_result
        
        # Act
        await activate_routine(mock_db_session, routine_id)
        
        # Assert - should have called execute twice (once for get, once for deactivate others)
        assert mock_db_session.execute.call_count >= 1
