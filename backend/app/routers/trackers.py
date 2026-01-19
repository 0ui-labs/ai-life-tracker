from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.auth import CurrentUser
from app.database import get_db
from app.models import Tracker, Entry
from app.schemas.tracker import (
    TrackerCreate,
    TrackerResponse,
    EntryCreate,
    EntryResponse,
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
    tracker_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tracker."""
    result = await db.execute(
        select(Tracker).where(Tracker.id == tracker_id)
    )
    tracker = result.scalar_one_or_none()
    if not tracker:
        raise HTTPException(status_code=404, detail="Tracker not found")
    return tracker


@router.get("/{tracker_id}/entries", response_model=list[EntryResponse])
async def list_entries(
    tracker_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """List entries for a tracker."""
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
    user_id = user.id
    
    db_entry = Entry(
        user_id=user_id,
        tracker_id=tracker_id,
        data=entry.data,
        notes=entry.notes,
        timestamp=entry.timestamp,
    )
    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)
    return db_entry
