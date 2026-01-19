from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser
from app.database import get_db
from app.models import Entry, Tracker
from app.schemas.tracker import (
    EntryCreate,
    EntryResponse,
    TrackerCreate,
    TrackerResponse,
    TrackerUpdate,
)
from app.services.user import get_or_create_user

router = APIRouter(prefix="/api/trackers", tags=["trackers"])


@router.get("", response_model=list[TrackerResponse])
async def list_trackers(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    """List all trackers for the current user."""
    user_id = user.id

    result = await db.execute(
        select(Tracker).where(Tracker.user_id == user_id)
    )
    return result.scalars().all()


@router.post("", response_model=TrackerResponse)
async def create_tracker(
    user: CurrentUser,
    tracker: TrackerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tracker."""
    # Ensure user exists in DB
    await get_or_create_user(db, user.id, user.email)
    user_id = user.id

    db_tracker = Tracker(
        user_id=user_id,
        name=tracker.name,
        category=tracker.category,
        schema=tracker.schema,
        icon=tracker.icon,
        color=tracker.color,
    )
    db.add(db_tracker)
    await db.commit()
    await db.refresh(db_tracker)
    return db_tracker


@router.get("/{tracker_id}", response_model=TrackerResponse)
async def get_tracker(
    user: CurrentUser,
    tracker_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tracker."""
    result = await db.execute(
        select(Tracker).where(Tracker.id == tracker_id, Tracker.user_id == user.id)
    )
    tracker = result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    return tracker


@router.put("/{tracker_id}", response_model=TrackerResponse)
async def update_tracker(
    user: CurrentUser,
    tracker_id: UUID,
    tracker_update: TrackerUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing tracker."""
    # Ensure user exists in DB
    await get_or_create_user(db, user.id, user.email)

    # Fetch the tracker
    result = await db.execute(select(Tracker).where(Tracker.id == tracker_id))
    tracker = result.scalar_one_or_none()

    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    # Check ownership
    if tracker.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this tracker")

    # Update only provided fields
    update_data = tracker_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tracker, field, value)

    await db.commit()
    await db.refresh(tracker)
    return tracker


@router.delete("/{tracker_id}")
async def delete_tracker(
    user: CurrentUser,
    tracker_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a tracker."""
    # Ensure user exists in DB
    await get_or_create_user(db, user.id, user.email)

    # Fetch the tracker
    result = await db.execute(select(Tracker).where(Tracker.id == tracker_id))
    tracker = result.scalar_one_or_none()

    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    # Check ownership
    if tracker.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this tracker")

    await db.delete(tracker)
    await db.commit()
    return {"message": "Tracker deleted successfully"}


@router.get("/{tracker_id}/entries", response_model=list[EntryResponse])
async def list_entries(
    user: CurrentUser,
    tracker_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List entries for a tracker."""
    # Verify tracker ownership
    tracker_result = await db.execute(
        select(Tracker).where(Tracker.id == tracker_id, Tracker.user_id == user.id)
    )
    tracker = tracker_result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    result = await db.execute(
        select(Entry)
        .where(Entry.tracker_id == tracker_id)
        .order_by(Entry.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{tracker_id}/entries", response_model=EntryResponse)
async def create_entry(
    user: CurrentUser,
    tracker_id: UUID,
    entry: EntryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new entry for a tracker."""
    # Ensure user exists in DB
    await get_or_create_user(db, user.id, user.email)

    # Verify tracker ownership
    tracker_result = await db.execute(
        select(Tracker).where(Tracker.id == tracker_id, Tracker.user_id == user.id)
    )
    tracker = tracker_result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")

    db_entry = Entry(
        user_id=user.id,
        tracker_id=tracker_id,
        data=entry.data,
        notes=entry.notes,
        timestamp=entry.timestamp,
    )
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry
