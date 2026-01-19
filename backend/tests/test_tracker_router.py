"""Tests for the Tracker Router endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.routers.trackers import (
    update_tracker,
    delete_tracker,
)


# =============================================================================
# Test Update Tracker
# =============================================================================


@pytest.mark.asyncio
async def test_update_tracker_updates_name_when_provided():
    """Updating a tracker with a new name should change the name."""
    # Arrange
    tracker_id = uuid4()
    mock_tracker = MagicMock()
    mock_tracker.id = tracker_id
    mock_tracker.name = "Old Name"
    mock_tracker.category = "fitness"
    mock_tracker.user_id = "test-user-123"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tracker

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"

    # Act
    from app.schemas.tracker import TrackerUpdate

    update_data = TrackerUpdate(name="New Name")

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        result = await update_tracker(
            user=mock_user,
            tracker_id=tracker_id,
            tracker_update=update_data,
            db=mock_db,
        )

    # Assert
    assert mock_tracker.name == "New Name"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_tracker_updates_multiple_fields():
    """Updating a tracker with multiple fields should update all of them."""
    # Arrange
    tracker_id = uuid4()
    mock_tracker = MagicMock()
    mock_tracker.id = tracker_id
    mock_tracker.name = "Old Name"
    mock_tracker.category = "fitness"
    mock_tracker.icon = None
    mock_tracker.color = None
    mock_tracker.user_id = "test-user-123"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tracker

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"

    # Act
    from app.schemas.tracker import TrackerUpdate

    update_data = TrackerUpdate(name="New Name", category="health", icon="heart", color="#FF0000")

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        result = await update_tracker(
            user=mock_user,
            tracker_id=tracker_id,
            tracker_update=update_data,
            db=mock_db,
        )

    # Assert
    assert mock_tracker.name == "New Name"
    assert mock_tracker.category == "health"
    assert mock_tracker.icon == "heart"
    assert mock_tracker.color == "#FF0000"


@pytest.mark.asyncio
async def test_update_tracker_returns_404_when_tracker_not_found():
    """Updating a non-existent tracker should raise 404 error."""
    # Arrange
    tracker_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"

    from app.schemas.tracker import TrackerUpdate

    update_data = TrackerUpdate(name="New Name")

    # Act & Assert
    from fastapi import HTTPException

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await update_tracker(
                user=mock_user,
                tracker_id=tracker_id,
                tracker_update=update_data,
                db=mock_db,
            )

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_update_tracker_returns_403_when_user_does_not_own_tracker():
    """Updating someone else's tracker should raise 403 error."""
    # Arrange
    tracker_id = uuid4()
    mock_tracker = MagicMock()
    mock_tracker.id = tracker_id
    mock_tracker.name = "Old Name"
    mock_tracker.user_id = "other-user-456"  # Different user owns this tracker

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tracker

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"  # Current user trying to update
    mock_user.email = "test@example.com"

    from app.schemas.tracker import TrackerUpdate

    update_data = TrackerUpdate(name="New Name")

    # Act & Assert
    from fastapi import HTTPException

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await update_tracker(
                user=mock_user,
                tracker_id=tracker_id,
                tracker_update=update_data,
                db=mock_db,
            )

    assert exc_info.value.status_code == 403


# =============================================================================
# Test Delete Tracker
# =============================================================================


@pytest.mark.asyncio
async def test_delete_tracker_removes_tracker_from_database():
    """Deleting a tracker should remove it from the database."""
    # Arrange
    tracker_id = uuid4()
    mock_tracker = MagicMock()
    mock_tracker.id = tracker_id
    mock_tracker.name = "To Delete"
    mock_tracker.user_id = "test-user-123"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tracker

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"

    # Act
    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        result = await delete_tracker(
            user=mock_user,
            tracker_id=tracker_id,
            db=mock_db,
        )

    # Assert
    mock_db.delete.assert_called_once_with(mock_tracker)
    mock_db.commit.assert_called_once()
    assert result == {"message": "Tracker deleted successfully"}


@pytest.mark.asyncio
async def test_delete_tracker_returns_404_when_tracker_not_found():
    """Deleting a non-existent tracker should raise 404 error."""
    # Arrange
    tracker_id = uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"
    mock_user.email = "test@example.com"

    # Act & Assert
    from fastapi import HTTPException

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await delete_tracker(
                user=mock_user,
                tracker_id=tracker_id,
                db=mock_db,
            )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_tracker_returns_403_when_user_does_not_own_tracker():
    """Deleting someone else's tracker should raise 403 error."""
    # Arrange
    tracker_id = uuid4()
    mock_tracker = MagicMock()
    mock_tracker.id = tracker_id
    mock_tracker.user_id = "other-user-456"  # Different user owns this tracker

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tracker

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    mock_user = MagicMock()
    mock_user.id = "test-user-123"  # Current user trying to delete
    mock_user.email = "test@example.com"

    # Act & Assert
    from fastapi import HTTPException

    with patch("app.routers.trackers.get_or_create_user", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await delete_tracker(
                user=mock_user,
                tracker_id=tracker_id,
                db=mock_db,
            )

    assert exc_info.value.status_code == 403
